#!/usr/bin/env bash
# A Go package with no frontend.
set -euo pipefail
cat > go.mod <<'FIXTURE'
module example.com/stats

go 1.23
FIXTURE
cat > stats.go <<'FIXTURE'
package stats

// Max returns the largest value of values, or 0 when values is empty.
func Max(values []int) int {
	if len(values) == 0 {
		return 0
	}
	max := values[0]
	for _, v := range values[1:] {
		if v > max {
			max = v
		}
	}
	return max
}
FIXTURE
