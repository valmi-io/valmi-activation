import os
connectors = {
    "destination-webhook": "0.1.14",
    "destination-stripe": "0.1.8",
    "destination-slack": "0.1.8",
    "destination-hubspot": "0.1.8",
    "destination-google-sheets": "0.1.8",
    "destination-google-ads": "0.1.8",
    "destination-gong": "0.1.8",
    "destination-facebook-ads": "0.1.8",
    "destination-customer-io": "0.1.8",
    "destination-android-push-notifications": "0.1.9",
             
    "source-redshift": "0.1.12",
    "source-snowflake": "0.1.12",
    "source-postgres": "0.1.12"
}

valmi_core = "0.1.15"

valmi_app_backend = "0.1.15"

valmi_app = "0.1.14"

def tag_and_push(tag_name, message):
    os.system("git tag -a %s -m '%s'" % (tag_name, message))
    os.system("git push origin %s" % tag_name)

def tag_valmi_app_backend():
    tag_name = 'valmi-app-backend/%s' % valmi_app_backend
    os.system("cd valmi-app-backend; git tag -a %s -m '%s'" % (tag_name, 'creating tag %s' % tag_name))
    os.system("cd valmi-app-backend; git push origin %s" % tag_name)

def tag_valmi_app():
    tag_name = 'valmi-app/%s' % valmi_app
    os.system("cd valmi-app; git tag -a %s -m '%s'" % (tag_name, 'creating tag %s' % tag_name))
    os.system("cd valmi-app; git push origin %s" % tag_name)

for k, v in connectors.items():
    print("Tagging connector %s:%s" % (k, v))
    tag_and_push("valmi-connector/%s/%s" % (k, v), "Tagging %s:%s" % (k, v))

tag_and_push("valmi-activation/%s" % valmi_core, "Tagging valmi-activation/%s" % valmi_core)
tag_valmi_app()
tag_valmi_app_backend()
