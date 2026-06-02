VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_TIME ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
LDFLAGS = -X main.Version=$(VERSION) -X main.BuildTime=$(BUILD_TIME)

.PHONY: build test test-e2e test-all clean

build:
	go build -ldflags "$(LDFLAGS)" -o bin/openwiki ./cmd/openwiki/

test:
	go test ./internal/...

test-e2e:
	go test ./tests/e2e/... -count=1

test-all: test test-e2e

clean:
	rm -rf bin/
