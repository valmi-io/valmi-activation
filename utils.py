import sys
import json
str = sys.stdin.read()
print(json.dumps({'json':str}))
