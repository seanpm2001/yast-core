#!/bin/bash

unset Y2DEBUG
unset Y2DEBUGGER

(./runag_anyagent -l - $1 >$2) 2>&1 | grep -F -v " <0> " | grep -v "^$" | sed 's/^....-..-.. ..:..:.. [^)]*) //g' > $3
