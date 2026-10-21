<?php
/* FreePBX adapter: JSON stdin/stdout is PRIVATE (create/ami return secrets).
 * Invoke only through queue_test.py. No SQL or generated configuration writes.
 */
error_reporting(E_ERROR);
ini_set('display_errors', '0');
ob_start();
try {
    $request = json_decode(file_get_contents('php://stdin'), true, 32, JSON_THROW_ON_ERROR);
    require '/etc/freepbx.conf';
    $core = FreePBX::Core();
    $queues = FreePBX::Queues();
    $op = $request['operation'];
    if ($op === 'ami') {
        $result = ['host' => $amp_conf['ASTMANAGERHOST'], 'port' => $amp_conf['ASTMANAGERPORT'],
                   'username' => $amp_conf['AMPMGRUSER'], 'secret' => $amp_conf['AMPMGRPASS']];
    } elseif ($op === 'log-cursor' || $op === 'queue-log') {
        // This instance writes queue_log through extconfig/ODBC rather than a file.
        $database = FreePBX::Database();
        $columns = $database->query('SHOW COLUMNS FROM asteriskcdrdb.queue_log')->fetchAll(PDO::FETCH_COLUMN);
        foreach (['id','time','callid','queuename','agent','event','data1','data2','data3'] as $column) {
            if (!in_array($column, $columns)) throw new Exception('queue_log schema');
        }
        if ($op === 'log-cursor') {
            $result = ['cursor'=>(int)$database->query('SELECT COALESCE(MAX(id),0) FROM asteriskcdrdb.queue_log')->fetchColumn()];
        } else {
            $queue = $request['queue'];
            if (!preg_match('/^[0-9]{4,10}$/D', $queue)) throw new Exception('queue');
            $statement = $database->prepare('SELECT time,callid,queuename AS queue,agent AS member,event,data1,data2,data3 FROM asteriskcdrdb.queue_log WHERE id > ? AND queuename = ? ORDER BY id LIMIT 1000');
            $statement->execute([(int)$request['cursor'], $queue]);
            $result = $statement->fetchAll(PDO::FETCH_ASSOC);
        }
    } else {
        $owner = $request['owner'];
        if (!preg_match('/^nvtest-[a-f0-9]{12}$/D', $owner)) throw new Exception('owner');
        $extensions = $request['extensions'];
        $queue = $request['queue'];
        if (count($extensions) < 3 || count($extensions) > 4) throw new Exception('extensions');
        $ids = array_merge($extensions, [$queue]);
        if (count(array_unique($ids)) !== count($ids)) throw new Exception('duplicate');
        foreach ($ids as $id) {
            if (!is_string($id) || !preg_match('/^[0-9]{4,10}$/D', $id)) throw new Exception('id');
        }
        if ($op === 'inspect') {
            $occupied = [];
            foreach ($ids as $id) {
                if (framework_check_extension_usage($id) || $core->getDevice($id) || queues_get($id)) $occupied[] = $id;
            }
            $result = ['occupied' => $occupied, 'extension_count' => count($core->listUsers()),
                       'queue_count' => count($queues->listQueues()),
                       'lazy_configurable' => false];
        } elseif ($op === 'create') {
            // Prove every number is unused before the first write.
            foreach ($ids as $id) {
                if (framework_check_extension_usage($id) || $core->getDevice($id) || queues_get($id)) throw new Exception('collision');
            }
            $accounts = [];
            foreach ($extensions as $extension) {
                $user = $core->generateDefaultUserSettings($extension, $owner);
                $user['ringtimer'] = (int)($request['extension_timeout'] ?? 5);
                $user['noanswer_dest'] = 'app-blackhole,hangup,1';
                $user['busy_dest'] = 'app-blackhole,hangup,1';
                foreach (['recording_in_internal','recording_out_internal','recording_in_external','recording_out_external'] as $key) {
                    $user[$key] = 'never';
                }
                $core->addUser($extension, $user);
                $device = $core->generateDefaultDeviceSettings('pjsip', $extension, $owner);
                $secret = bin2hex(random_bytes(24));
                foreach (['secret' => $secret, 'transport' => '0.0.0.0-udp',
                          'outbound_proxy' => $request['endpoint_proxy'], 'rewrite_contact' => 'no',
                          'force_rport' => 'no', 'rtp_symmetric' => 'yes', 'qualifyfreq' => '0',
                          'disallow' => 'all', 'allow' => 'ulaw,alaw', 'max_contacts' => '1'] as $key => $value) {
                    $device[$key]['value'] = $value;
                }
                $core->addDevice($extension, 'pjsip', $device);
                $accounts[] = ['username' => $extension, 'password' => $secret];
            }
            $request['operation'] = 'configure';
            $op = 'configure';
        } elseif ($op === 'delete' || $op === 'verify') {
            // Never remove another fixture's configuration, including after a partial create.
            $q = queues_get($queue);
            if ($q && $q['name'] !== $owner) throw new Exception('queue owner');
            $owned = [];
            foreach ($extensions as $extension) {
                $u = $core->getUser($extension);
                $d = $core->getDevice($extension);
                if ($u && $u['name'] !== $owner) throw new Exception('user owner');
                if ($d && $d['description'] !== $owner) throw new Exception('device owner');
                if ($u || $d) $owned[] = $extension;
            }
            if ($op === 'delete') {
                if ($q) queues_del($queue);
                foreach (array_reverse($extensions) as $extension) {
                    if ($core->getDevice($extension)) $core->delDevice($extension);
                    if ($core->getUser($extension)) $core->delUser($extension);
                }
                needreload();
                $result = ['removed' => true];
            } else {
                $result = ['verified' => true, 'owned_extensions' => $owned];
            }
        }
        if ($op === 'configure') {
            $q = queues_get($queue);
            if ($q && $q['name'] !== $owner) throw new Exception('queue owner');
            $strategy = $request['strategy'] ?? 'linear';
            if (!in_array($strategy, ['linear','rrmemory','ringall','leastrecent','fewestcalls','random','rrordered','wrandom'])) throw new Exception('strategy');
            if (!empty($request['lazy'])) throw new Exception('Lazy Members not exposed by installed FreePBX API');
            foreach (['ring_timeout','retry','maxwait'] as $key) {
                if (!isset($request[$key]) || !is_int($request[$key]) || $request[$key] < 1 || $request[$key] > 300) throw new Exception('interval');
            }
            $autopause = $request['autopause'] ?? 'no';
            if (!in_array($autopause, ['no','yes','all'])) throw new Exception('autopause');
            if ($q) queues_del($queue);
            $_REQUEST = ['action'=>'add', 'strategy'=>$strategy, 'timeout'=>$request['ring_timeout'],
                        'retry'=>$request['retry'], 'autopause'=>$autopause, 'maxlen'=>'0',
                        'joinempty'=>'yes', 'leavewhenempty'=>'no', 'wrapuptime'=>'0',
                        'announcefreq'=>'0', 'min-announce'=>'15', 'announceholdtime'=>'no',
                        'announceposition'=>'no', 'recording'=>'dontcare', 'cron_schedule'=>'never'];
            // Dynamic members are added in the runner through AMI in explicit order.
            queues_add($queue, $owner, '', '', 'app-blackhole,hangup,1', '', [], '',
                       $request['maxwait'], '', empty($request['ringinuse']) ? '2' : '0',
                       '', '0', '0', [], 'no');
            needreload();
            $actual = queues_get($queue);
            $result = ['configured'=>true, 'queue'=> $queue,
                       'settings'=>array_intersect_key($actual, array_flip(['strategy','timeout','retry','ringinuse','autopause'])),
                       'lazy_configurable'=>false];
            if (isset($accounts)) $result['accounts'] = $accounts;
        }
        if (!isset($result)) throw new Exception('operation');
    }
    ob_end_clean();
    echo json_encode($result, JSON_THROW_ON_ERROR);
} catch (Throwable $error) {
    ob_end_clean();
    fwrite(STDERR, "FreePBX fixture operation failed (details withheld)\n");
    exit(1);
}
