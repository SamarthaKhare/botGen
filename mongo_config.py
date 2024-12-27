MONGO_CONFIG = {
    "_id": "65d831cbe148984efe42b9dd",
    "key": "CPUMEMORY_REMEDIATION_CONFIG",
    "CPUMemoryResourceRemediation": {
        "WIP": {
            "EMAIL_CONTENT": "<table><tr><td><b style='font-size:14px;color:#0B2A46'> {INCIDENT_ID} - Status - Work In Progress </b></td></tr></table><hr style='height:2px;background-color:#0B2A46;width:99%'><div>Dear Team,<br /><br />ZIF Remediate has started remediate process on {DEVICE_NAME} for {INCIDENT_ID} and will resolve the incident with remediate status. Incident in Resolved state will automatically get closed after 2 business days.<br /></n> <br/> <br/><b>Thank you,<br/>ZIF Remediate Team<br/>(Powered by ZIF Remediate - IT Process Automation Platform)</b><br/><hr size='1' style='width:99%'> <span style='font-style:italic'>This is an auto-generated mailer from ZIF Remediate. In case you have queries about this mail, please reach out to ZIF Remediate support Team instead of replying to it.</span><br /><br /></div>",
            "EMAIL_SUBJECT": "{INCIDENT_ID} - ZIF Remediate has started the remediation for {ALERT_TYPE} high utilization on {DEVICE_NAME}",
            "INCIDENT_PAYLOAD": {
                "state": "2",
                "close_code": "Break/Fix",
            }
        },
        "RESOLVED": {
            "EMAIL_CONTENT": "<table><tr><td><b style='font-size:14px;color:#0B2A46'> {INCIDENT_ID} - Status - Resolved </b></td></tr></table><hr style='height:2px;background-color:#0B2A46;width:99%'><div>Dear Team,<br /><br />ZIF Remediate has resolved the incident by considering the current {ALERT_TYPE} utilization {TOTAL_USAGE} % which is below the defined threshold level {THRESHOLD_VALUE} %. <br /><br />Incident in Resolved state will automatically get closed after 2 business days.<br /></n> <br/> <br/><b>Thank you,<br/>ZIF Remediate Team<br/>(Powered by ZIF Remediate - IT Process Automation Platform)</b><br/><hr size='1' style='width:99%'> <span style='font-style:italic'>This is an auto-generated mailer from ZIF Remediate. In case you have queries about this mail, please reach out to ZIF Remediate support Team instead of replying to it.</span><br /><br /></div>",
            "EMAIL_SUBJECT": "{INCIDENT_ID} -Resolved by ZIFRemediate",
            "INCIDENT_PAYLOAD": {
                "state": "6",
                "close_code": "Break/Fix",
                "u_sop": "Yes",
                "close_notes": "ZIF Remediate completed its action on high resource ({ALERT_TYPE}) usage alert and incident is resolved with appropriate work notes.",
                "work_notes": "ZIF Remediate has resolved the incident by considering the current {ALERT_TYPE} utilization.({TOTAL_USAGE}%) which is below the defined threshold level ({THRESHOLD_VALUE}%)."
            }
        },
        "ESCALATE": {
            "EMAIL_CONTENT": "<table style='width: 60%; font-size: 12px; border-collapse: collapse;'><tr><td><b style='font-size:14px;color:#0B2A46'> {INCIDENT_ID} - Status - Work In Progress </b></td></tr></table><hr style='height:2px;background-color:#0B2A46;width:99%'><div>Dear Team,<br /><br />ZIF Remediate has found the top 5 process utilizing more {ALERT_TYPE} in the device {DEVICE_NAME}. Please find the below process list to overcome high {ALERT_TYPE} utilization.<br /><table cellpadding='11' cellspacing='0' border='1' width='100%' rules='all' style='border-collapse:collapse'><tr style='background-color:navy; color:white'><th style='font-family:calibri,tahoma,verdana;text-align:left;'>S.No</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>Process ID</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>Process Name</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>{ALERT_TYPE} value</th></tr>{PROCESS_RESULT}</table><br/> <br/><b>Thank you,<br/>ZIF Remediate Team<br/>(Powered by ZIF Remediate - IT Process Automation Platform)</b><br/><hr size='1' style='width:99%'> <span style='font-style:italic'>This is an auto-generated mailer from ZIF Remediate. In case you have queries about this mail, please reach out to ZIF Remediate support Team instead of replying to it.</span><br /><br /></div>",
            "EMAIL_SUBJECT": "{INCIDENT_ID} has been escalated to {RESOLVER} group by ZIF Remediate",
            "INCIDENT_PAYLOAD": {
                "work_notes": "[code]<table style='width: 60%; font-size: 12px; border-collapse: collapse;'><tr><td><b style='font-size:14px;color:#0B2A46'><div><br /><br />Incident has been escalated to '{RESOLVER}' group.Top 5 talkers of high {ALERT_TYPE} usage (resource consuming processes) are listed below from the reported device '{DEVICE_NAME}'.<br /><table cellpadding='11' cellspacing='0' border='1' width='100%' rules='all' style='border-collapse:collapse'><tr style='background-color:rgb(171,171,180); color:rgb(17,17,17); height:20px;'><th style='font-family:calibri,tahoma,verdana;text-align:left;'>S.No</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>Process ID</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>Process Name</th><th style='font-family:calibri,tahoma,verdana;text-align:left;'>{ALERT_TYPE} value</th></tr>{PROCESS_RESULT}</table><br/> <br/><br /><br /></div></td></tr></table>[/code]",
                "close_code": "Break/Fix"
            }
        },
        "ESCALATE_DEVICE_UNREACHABLE": {
            "EMAIL_CONTENT": "<table><tr><td><b style='font-size:14px;color:#0B2A46'> {INCIDENT_ID} - Status - Work In Progress </b></td></tr></table><hr style='height:2px;background-color:#0B2A46;width:99%'><div>Dear Team,<br /><br />ZIF Remediate has initiated the incident {INCIDENT_ID} and after 3 consecutive attempt the Device {DEVICE_NAME} is not reachable due to {FAILURE_TYPE} failure.<br /> <br />Requesting {RESOLVER} Team to work on this incident.<br /></n> <br/> <br/><b>Thank you,<br/>ZIF Remediate Team<br/>(Powered by ZIF Remediate - IT Process Automation Platform)</b><br/><hr size='1' style='width:99%'> <span style='font-style:italic'>This is an auto-generated mailer from ZIF Remediate. In case you have queries about this mail, please reach out to ZIF Remediate support Team instead of replying to it.</span><br /><br /></div>",
            "EMAIL_SUBJECT": "{INCIDENT_ID} has been escalated to {RESOLVER} group by ZIF Remediate",
            "INCIDENT_PAYLOAD": {
                "work_notes": "After 3 consecutive attempt the Device {DEVICE_NAME} is not reachable due to {FAILURE_TYPE}.",
                "close_code": "Break/Fix"
            }
        },
        "ESCALATE_CLUSTER_SERVERS": {
            "EMAIL_CONTENT": "<table><tr><td><b style='font-size:14px;color:#0B2A46'> {INCIDENT_ID} - Status - Work In Progress </b></td></tr></table><hr style='height:2px;background-color:#0B2A46;width:99%'><div>Dear Team,<br /><br />ZIF Remediate has escalated the incident {INCIDENT_ID} to '{RESOLVER}' group since '{DEVICE_NAME}' is found to be a cluster.<br /> <br />Requesting {RESOLVER} Team to work on this incident.<br /></n> <br/> <br/><b>Thank you,<br/>ZIF Remediate Team<br/>(Powered by ZIF Remediate - IT Process Automation Platform)</b><br/><hr size='1' style='width:99%'> <span style='font-style:italic'>This is an auto-generated mailer from ZIF Remediate. In case you have queries about this mail, please reach out to ZIF Remediate support Team instead of replying to it.</span><br /><br /></div>",
            "EMAIL_SUBJECT": "{INCIDENT_ID} has been escalated to {RESOLVER} group by ZIF Remediate",
            "INCIDENT_PAYLOAD": {
                "work_notes": "Device {DEVICE_NAME} is found to be a cluster. Hence it is escalated to {RESOLVER} Team.",
                "close_code": "Break/Fix"
            }
        }
    },
    "ServiceRestartRemediation": {
    "WIP": {
        "INCIDENT_PAYLOAD": {
            "state": "2",
            "work_notes":"Picked for remediation"
        }
    },
    "RESOLVED": {
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate successfully restarted the affected service to resolve the issue. Incident is resolved with relevant updates.",
            "work_notes": "ZIF Remediate identified the issue and successfully restarted the service {SERVICE_NAME} on {DEVICE_NAME}."
        }
    },
    "ESCALATE_DEVICE_UNREACHABLE": {
        "INCIDENT_PAYLOAD": {
            "work_notes": "After 3 consecutive attempts, the device {DEVICE_NAME} is not reachable due to {FAILURE_TYPE}.",
            "close_code": "Break/Fix"
        }
    },
   "RUNNING":{
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate has resolved the issue with relevant updates.Provided service {SERVICE_NAME} was already running.",
            "work_notes":"ZIF Remediate has checked the issues-{SERVICE_NAME} service was already running"
        }
    },
    "RESTART_FAILURE":{
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate has attempted to restart the service {SERVICE_NAME} on {DEVICE_NAME} in incident but failed and thus it has been escalated",
            "work_notes":"ZIF Remediate is unable to restart the service {SERVICE_NAME} on {DEVICE_NAME}"
        }
    }
},"PingResponseRemediation": {
    "WIP": {
        "INCIDENT_PAYLOAD": {
            "state": "2",
            "work_notes":"Picked for remediation"
        }
    },
    "RESOLVED": {
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate successfully restarted the affected service to resolve the issue. Incident is resolved",
            "work_notes": "ZIF Remediate identified the issue and successfully restarted the service {SERVICE_NAME} on {DEVICE_NAME} and following is the ping result {PROCESS_RESULT}."
        }
    },
    "ESCALATE_DEVICE_UNREACHABLE": {
        "INCIDENT_PAYLOAD": {
            "work_notes": "After 3 consecutive attempts, the device {DEVICE_NAME} is not reachable due to {FAILURE_TYPE}.",
            "close_code": "Break/Fix"
        }
    },
   "RUNNING":{
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate has resolved the issue with relevant updates.Provided service {SERVICE_NAME} was already running.",
            "work_notes":"ZIF Remediate has checked the issues-{SERVICE_NAME} service was already running and following is the ping result {PROCESS_RESULT}"
        }
    },
    "RESTART_FAILURE":{
        "INCIDENT_PAYLOAD": {
            "state": "6",
            "close_code": "Break/Fix",
            "u_sop": "Yes",
            "close_notes": "ZIF Remediate has attempted to restart the service {SERVICE_NAME} on {DEVICE_NAME} in incident but failed and thus it has been escalated ",
            "work_notes":"ZIF Remediate is unable to restart the service {SERVICE_NAME} on {DEVICE_NAME} and following is the ping result {PROCESS_RESULT}"
        }
    }
}
}




