#!/bin/bash

diff=$(git diff --name-status "$@")
if [ $? -eq 128 ]; then
	echo "Failed to diff"
	exit 1
fi

if echo "$diff" | grep '^[^A]'; then
	echo "Only additions are allowed!"
	exit 1
fi
