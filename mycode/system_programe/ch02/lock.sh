#!/bin/bash

#bin/lock_read s.txt & 
bin/lock_write s.txt ABCDERGHIJKLMN  lock &
bin/lock_write s.txt 12345678901234  lock & 
bin/lock_write s.txt gaskgjaglkaglag  lock &
