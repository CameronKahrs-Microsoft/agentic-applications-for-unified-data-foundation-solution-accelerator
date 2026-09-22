import os
import json
import random
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF

random.seed(42)

output_dir = r"C:/Git/agentic-applications-for-unified-data-foundation-solution-accelerator/data/20260922_113709_telecommunications"
config_dir = os.path.join(output_dir, "config")
tables_dir = os.path.join(output_dir, "tables")
documents_dir = os.path.join(output_dir, "documents")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)
os.makedirs(documents_dir, exist_ok=True)

today = datetime.now()

NUM_OUTAGES = 16
NUM_TICKETS = 40

outage_ids = [f"OUT{str(i).zfill(3)}" for i in range(1, NUM_OUTAGES + 1)]
ticket_ids = [f"TCK{str(i).zfill(3)}" for i in range(1, NUM_TICKETS + 1)]

regions = ["North", "South", "East", "West", "Central"]
severities = ["Critical", "High", "Medium", "Low"]
service_types = ["Mobile Voice", "Mobile Data", "Fixed Internet", "VoIP", "TV"]
ticket_statuses = ["Open", "In Progress", "Resolved", "Closed"]
root_causes = ["Fiber Cut", "Power Failure", "Router Fault", "Software Bug", "Weather", "Human Error"]
priority_levels = ["P1", "P2", "P3", "P4"]
channels = ["Phone", "Portal", "Email", "NOC Alert"]

outage_reported = []
outage_restored = []
outage_duration_hours = []
for i in range(NUM_OUTAGES):
    if i < int(NUM_OUTAGES * 0.75):
        days_ago = random.randint(1, 90)
        duration = random.randint(1, 6)
    else:
        days_ago = random.randint(1, 180)
        duration = random.randint(7, 18)
    start_dt = today - timedelta(days=days_ago)
    outage_reported.append(start_dt.strftime("%Y-%m-%d"))
    outage_restored.append((start_dt + timedelta(hours=duration)).strftime("%Y-%m-%d"))
    outage_duration_hours.append(duration)

outages = pd.DataFrame({
    "outage_id": outage_ids,
    "region": [regions[i % len(regions)] for i in range(NUM_OUTAGES)],
    "service_type": [service_types[i % len(service_types)] for i in range(NUM_OUTAGES)],
    "severity": random.choices(severities, weights=[2, 3, 4, 3], k=NUM_OUTAGES),
    "root_cause": random.choices(root_causes, weights=[3, 2, 3, 2, 2, 1], k=NUM_OUTAGES),
    "reported_date": outage_reported,
    "restored_date": outage_restored,
    "duration_hours": outage_duration_hours,
    "customers_affected": [random.randint(500, 2500) if i < 12 else random.randint(2600, 8000) for i in range(NUM_OUTAGES)],
    "status": [random.choices(["Resolved", "Closed"], weights=[7, 3], k=1)[0] if i < 14 else random.choice(["Resolved", "Closed"]) for i in range(NUM_OUTAGES)]
})

ticket_created = []
ticket_resolved = []
ticket_response_hours = []
ticket_resolution_hours = []
ticket_sla_breached = []
for i in range(NUM_TICKETS):
    if i < int(NUM_TICKETS * 0.7):
        created_days_ago = random.randint(0, 60)
        response = random.randint(1, 18)
        resolution = random.randint(2, 40)
        breached = False
    else:
        created_days_ago = random.randint(0, 120)
        response = random.randint(25, 72)
        resolution = random.randint(48, 120)
        breached = True
    created_dt = today - timedelta(days=created_days_ago)
    ticket_created.append(created_dt.strftime("%Y-%m-%d"))
    ticket_resolved.append((created_dt + timedelta(hours=resolution)).strftime("%Y-%m-%d"))
    ticket_response_hours.append(response)
    ticket_resolution_hours.append(resolution)
    ticket_sla_breached.append(breached)

tickets = pd.DataFrame({
    "ticket_id": ticket_ids,
    "outage_id": [random.choice(outage_ids) for _ in range(NUM_TICKETS)],
    "customer_segment": random.choices(["Consumer", "Small Business", "Enterprise", "Wholesale"], weights=[4, 3, 2, 1], k=NUM_TICKETS),
    "priority": random.choices(priority_levels, weights=[1, 2, 4, 3], k=NUM_TICKETS),
    "channel": random.choices(channels, weights=[3, 4, 2, 3], k=NUM_TICKETS),
    "status": random.choices(ticket_statuses, weights=[2, 2, 4, 2], k=NUM_TICKETS),
    "created_date": ticket_created,
    "resolved_date": ticket_resolved,
    "response_time_hours": ticket_response_hours,
    "resolution_time_hours": ticket_resolution_hours,
    "sla_breached": ticket_sla_breached
})

outages.to_csv(os.path.join(tables_dir, "network_outages.csv"), index=False)
tickets.to_csv(os.path.join(tables_dir, "trouble_tickets.csv"), index=False)

config = {
    "scenario": "telecommunications",
    "name": "Telecommunications Network Operations",
    "description": "Network operations sample data for outage tracking and trouble ticket management",
    "tables": {
        "network_outages": {
            "columns": ["outage_id", "region", "service_type", "severity", "root_cause", "reported_date", "restored_date", "duration_hours", "customers_affected", "status"],
            "types": {
                "outage_id": "String",
                "region": "String",
                "service_type": "String",
                "severity": "String",
                "root_cause": "String",
                "reported_date": "Date",
                "restored_date": "Date",
                "duration_hours": "BigInt",
                "customers_affected": "BigInt",
                "status": "String"
            },
            "key": "outage_id",
            "source_table": "network_outages"
        },
        "trouble_tickets": {
            "columns": ["ticket_id", "outage_id", "customer_segment", "priority", "channel", "status", "created_date", "resolved_date", "response_time_hours", "resolution_time_hours", "sla_breached"],
            "types": {
                "ticket_id": "String",
                "outage_id": "String",
                "customer_segment": "String",
                "priority": "String",
                "channel": "String",
                "status": "String",
                "created_date": "Date",
                "resolved_date": "Date",
                "response_time_hours": "BigInt",
                "resolution_time_hours": "BigInt",
                "sla_breached": "Boolean"
            },
            "key": "ticket_id",
            "source_table": "trouble_tickets"
        }
    },
    "relationships": [
        {"name": "outage_ticket", "from": "trouble_tickets", "to": "network_outages", "fromKey": "outage_id", "toKey": "outage_id"}
    ]
}

with open(os.path.join(config_dir, "ontology_config.json"), "w") as f:
    json.dump(config, f, indent=4)

def create_pdf(title, sections, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    for heading, content in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        content = content.encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(0, 6, content)
        pdf.ln(5)
    pdf.output(os.path.join(documents_dir, filename))

network_sections = [
    ("1. Incident Classification",
     "All network incidents must be classified by severity within 15 minutes of detection. Critical incidents affect core routing, broadband backhaul, or mobile authentication. High incidents involve regional service degradation with potential customer impact. Medium incidents are localized and usually affect a single node or access segment. Low incidents are informational and should be monitored until resolution."),
    ("2. Restoration Targets",
     "Critical outages require restoration work to begin immediately and service restoration should be completed within 4 hours whenever possible. High severity incidents must be restored within 8 hours. Medium severity incidents should be resolved within 24 hours. Low severity incidents can remain under observation, but every case must have an assigned owner and a documented update at least once per business day."),
    ("3. Escalation Rules",
     "If a Major Service Outage affects more than 2,500 customers or spans more than one region, the case must be escalated to the Network Operations Director. Escalation must occur within 30 minutes of confirmation. The incident bridge must remain open until service has stabilized and no new alarms are observed for 20 consecutive minutes."),
    ("4. Communication Cadence",
     "Customer communications must be issued every 60 minutes for unresolved Critical incidents and every 2 hours for High incidents. Internal leadership updates are required at the top of each hour during active incidents. Status messages must include impacted services, estimated restoration time, and the next update time. All timestamps must be recorded in the incident log."),
    ("5. Root Cause Review",
     "Every outage longer than 6 hours requires a root cause review within 5 business days. The review must identify the triggering event, the failing component, and any missed preventive control. Corrective actions must include a due date, an owner, and a validation step. Repeat incidents on the same network element require a second review by engineering."),
    ("6. Closure Criteria",
     "An outage may be closed only after service verification, customer impact assessment, and documentation of the final fix. The incident record must include the restored timestamp, the final status, and a summary of monitoring performed after restoration. If alarms recur within 24 hours, the outage must be reopened and linked to the original record."),
    ("7. Monitoring Standards",
     "Network monitoring teams must review core performance dashboards every 15 minutes. Packet loss above 2 percent, latency above 120 milliseconds, or repeated authentication failures must be treated as actionable signals. When these thresholds are observed, the operations analyst must create or update an incident ticket and notify the on-call engineer immediately.")
]
create_pdf("Network Operations Incident Management Policy", network_sections, "network_operations_incident_policy.pdf")

ticket_sections = [
    ("1. Ticket Intake",
     "All customer trouble reports must be logged as a ticket within 10 minutes of receipt. Each ticket must include the affected service, a contact channel, a priority, and a link to any related outage. Tickets created outside business hours are still subject to the same logging standard. Duplicate reports should be merged only after the related customer contacts are recorded."),
    ("2. Response Targets",
     "P1 tickets require an initial response within 1 hour. P2 tickets require response within 4 hours. P3 tickets require response within 8 hours. P4 tickets require response within 24 hours. If the ticket is tied to a known outage, the response note must explain the outage linkage and the expected restoration window. Exceptions require manager approval."),
    ("3. Resolution Expectations",
     "Priority 1 issues should be resolved within 8 hours whenever the cause is already known. Priority 2 issues should be resolved within 24 hours. Priority 3 issues should be resolved within 72 hours. Priority 4 issues should be resolved within 5 business days. Any case at risk of breach must be flagged in the daily queue review and assigned a next action."),
    ("4. Escalation and Ownership",
     "Tickets that exceed response or resolution targets must be escalated to the next support tier. Ownership must be transferred with a written summary, troubleshooting steps already attempted, and the next diagnostic action. Escalated cases require acknowledgment within 30 minutes. If the customer is enterprise or wholesale, account management must be informed before the escalation is closed."),
    ("5. Status Management",
     "Ticket statuses must follow Open, In Progress, Resolved, and Closed. Resolved status indicates that the service is restored and the customer has been notified. Closed status means all internal notes are complete and no further action is expected. Tickets may not move directly from Open to Closed unless a documented waiver is approved by the operations manager."),
    ("6. SLA Breach Handling",
     "Any ticket with a response time above the target or a resolution time above the target is considered an SLA breach. Breached tickets require a post-incident note within one business day and must be reviewed during the weekly service meeting. Repeated breaches from the same service area require a corrective action plan with measurable milestones."),
    ("7. Reporting Requirements",
     "Operations reports must summarize open tickets, breached tickets, average response time, and average resolution time by priority and by channel. The weekly report must also identify the top three outage-linked ticket groups. Leadership uses this report to confirm whether service levels are improving and whether staffing changes are needed.")
]
create_pdf("Trouble Ticket Handling Standard", ticket_sections, "trouble_ticket_handling_standard.pdf")

service_sections = [
    ("1. Major Service Outage Definition",
     "A Major Service Outage exists when a service event affects more than 2,500 customers, lasts longer than 4 hours, or impacts at least two regions. Once declared, the incident commander must assign a bridge lead, a communications lead, and a technical lead. The declaration must be logged in the operations system with a unique incident reference."),
    ("2. Command Bridge Procedures",
     "The command bridge must open within 15 minutes of the Major Service Outage declaration. Participants must join with name, role, and organization. The bridge lead records decisions, action owners, and update times. If the outage continues beyond 6 hours, a senior manager must join the bridge and confirm the next restoration milestone."),
    ("3. Customer Update Policy",
     "Public and direct customer updates must be issued at least every 2 hours during a Major Service Outage. Each update must explain the current status, the services affected, the estimated time to restore, and the next communication time. If restoration timing changes by more than 30 minutes, a revised update must be issued immediately."),
    ("4. Network Verification",
     "Before closing a major incident, network teams must verify service restoration using live alarms, synthetic tests, and customer confirmations where available. Verification must continue for 30 minutes after the primary fix is applied. If alarms return during verification, the outage remains open and the recovery steps must be repeated."),
    ("5. Documentation Standards",
     "Every major incident requires a final report within 2 business days. The report must include the impact summary, timeline, root cause, fix applied, lessons learned, and preventive actions. The final report should use plain language so both technical and business teams can review it quickly. All time references must be consistent across the report."),
    ("6. Preventive Actions",
     "Preventive actions from major incident reviews must be assigned to a named owner and tracked until completion. Actions are expected to reduce repeat events, improve monitoring coverage, or shorten restoration time. Each action should include a due date no more than 30 days after approval, unless leadership approves an extension in writing."),
    ("7. Review Cadence",
     "The major incident process is reviewed monthly by network operations leadership. Trends in outage duration, customer impact, and ticket escalation volume are assessed to identify where procedures need refinement. If two or more Major Service Outages occur in the same region during a 60 day period, the regional escalation playbook must be updated.")
]
create_pdf("Major Service Outage Response Guide", service_sections, "major_service_outage_response_guide.pdf")

with open(os.path.join(config_dir, "sample_questions.txt"), "w") as f:
    f.write("=== SQL QUESTIONS (Fabric Data) ===\n")
    f.write("1. How many network outages were recorded for each region?\n")
    f.write("2. What is the average duration_hours for outages by severity?\n")
    f.write("3. Which service_type has the highest total customers_affected?\n")
    f.write("4. How many trouble_tickets have status = 'Open' or 'In Progress'?\n")
    f.write("5. What is the monthly breakdown of tickets by priority using created_date?\n")
    f.write("\n")
    f.write("=== DOCUMENT QUESTIONS (AI Search) ===\n")
    f.write("1. What is the required restoration target for Critical incidents in the Network Operations Incident Management Policy?\n")
    f.write("2. How often must customer updates be issued during an unresolved High incident?\n")
    f.write("3. What response targets apply to P1, P2, P3, and P4 tickets in the Trouble Ticket Handling Standard?\n")
    f.write("4. When does a Major Service Outage need to be escalated to the Network Operations Director?\n")
    f.write("5. What are the closure criteria for an outage before it can be marked as closed?\n")
    f.write("\n")
    f.write("=== COMBINED INSIGHT QUESTIONS ===\n")
    f.write("1. Are any trouble_tickets in breach of the response targets described in the Trouble Ticket Handling Standard?\n")
    f.write("2. Do any network_outages exceed the restoration target described in the Network Operations Incident Management Policy?\n")
    f.write("3. Which trouble_tickets linked to outages have resolution_time_hours that conflict with the resolution expectations in the Trouble Ticket Handling Standard?\n")
    f.write("4. Are there outages with customers_affected levels that require escalation under the Major Service Outage Response Guide?\n")
    f.write("5. Which severity levels have the most outages that would fail the restoration standards in the Network Operations Incident Management Policy?\n")

print("Telecommunications sample data generation complete.")