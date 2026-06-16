import json

import main as layla_report


def handler(event, context):
    layla_report.main()
    return json.dumps({"status": "ok"}, ensure_ascii=False)
