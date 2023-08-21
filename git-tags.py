import os
connectors = {
    "destination-webhook": "0.1.10",
    "destination-stripe": "0.1.5",
    "destination-slack": "0.1.5",
    "destination-hubspot": "0.1.5",
    "destination-google-sheets": "0.1.5",
    "destination-google-ads": "0.1.5",
    "destination-gong": "0.1.5",
    "destination-facebook-ads": "0.1.5",
    "destination-customer-io": "0.1.5",
    "destination-android-push-notifications": "0.1.6",
                                        
    "source-redshift": "0.1.8",
    "source-snowflake": "0.1.8",
    "source-postgres": "0.1.8"
}

valmi_core = "0.1.13"


def tag_and_push(tag_name, message):
    os.system("git tag -a %s -m '%s'" % (tag_name, message))
    os.system("git push origin %s" % tag_name)


for k, v in connectors.items():
    print("Tagging connector %s:%s" % (k, v))
    tag_and_push("valmi-connector/%s/%s" % (k, v), "Tagging %s:%s" % (k, v))

tag_and_push("valmi-activation/%s" % valmi_core, "Tagging valmi-activation/%s" % valmi_core)