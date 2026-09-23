"""
LLM Analyzer module for Software Requirement Analysis Agent.
Handles API invocation, JSON parsing, error handling, and offline viva demo mode.
"""
import os
import json
import re
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

from src.prompts import SYSTEM_PROMPT, ANALYSIS_USER_PROMPT
from src.validators import validate_analysis_data

load_dotenv()


# Built-in offline datasets for flawless viva demonstrations
DEMO_DATASETS = {
    "food_delivery": {
        "system_overview": {
            "system_name": "Online Food Delivery Platform (QuickBite)",
            "summary": "A comprehensive multi-tier food ordering and dispatching platform connecting customers, restaurants, delivery partners, and administrative staff.",
            "scope": "Covers customer registration, menu browsing, cart management, payment processing, real-time GPS delivery tracking, restaurant menu management, and administrative control. Hardware POS integration is out of scope for v1.0."
        },
        "system_features": [
            {"feature_id": "SF-001", "name": "User Account & Authentication", "description": "Secure customer, restaurant, and admin registration and role-based login."},
            {"feature_id": "SF-002", "name": "Restaurant & Menu Management", "description": "Restaurant onboarding, menu item listing, pricing, and live availability toggling."},
            {"feature_id": "SF-003", "name": "Order Lifecycle & Cart", "description": "Cart calculation, checkout, payment gateway integration, and order status transitions."},
            {"feature_id": "SF-004", "name": "Live Dispatch & Tracking", "description": "Real-time delivery partner assignment and geolocation tracking on map interfaces."},
            {"feature_id": "SF-005", "name": "Administrative Oversight", "description": "System analytics, dispute handling, restaurant vetting, and user management."}
        ],
        "functional_requirements": [
            {"id": "FR-001", "description": "The system shall allow new customers to register using email and verified phone number.", "category": "Authentication", "priority": "High", "rationale": "Essential for customer identification and communication."},
            {"id": "FR-002", "description": "The system shall authenticate users via credentials with session token issuance.", "category": "Authentication", "priority": "High", "rationale": "Protects user data and enforces role-based access."},
            {"id": "FR-003", "description": "The system shall allow customers to search and filter restaurants by cuisine, rating, and location.", "category": "Catalog", "priority": "High", "rationale": "Enables customers to discover food items quickly."},
            {"id": "FR-004", "description": "The system shall maintain a shopping cart per customer with real-time tax and delivery fee calculation.", "category": "Cart & Checkout", "priority": "High", "rationale": "Ensures transparent pricing before payment."},
            {"id": "FR-005", "description": "The system shall process online payments via integrated secure payment gateways.", "category": "Payments", "priority": "High", "rationale": "Facilitates cashless digital transactions."},
            {"id": "FR-006", "description": "The system shall provide real-time order status updates (Placed, Preparing, Out for Delivery, Delivered).", "category": "Tracking", "priority": "Medium", "rationale": "Keeps customers informed and reduces support inquiries."},
            {"id": "FR-007", "description": "The system shall allow restaurant managers to add, edit, and deactivate menu items and prices.", "category": "Restaurant Management", "priority": "High", "rationale": "Restaurants must manage inventory and pricing dynamically."},
            {"id": "FR-008", "description": "The system shall allow administrators to activate, suspend, and audit restaurant and user accounts.", "category": "Administration", "priority": "Medium", "rationale": "Ensures platform compliance and safety."}
        ],
        "non_functional_requirements": [
            {"id": "NFR-001", "category": "Performance", "description": "The system shall render restaurant search results within 1.5 seconds under 10,000 concurrent requests.", "priority": "High", "metric": "Latency <= 1500ms at 95th percentile"},
            {"id": "NFR-002", "category": "Security", "description": "The system shall encrypt all sensitive customer data at rest (AES-256) and in transit (TLS 1.3).", "priority": "High", "metric": "100% compliance with TLS 1.3 & AES-256"},
            {"id": "NFR-003", "category": "Reliability", "description": "The system shall maintain an operational uptime of 99.9% excluding planned maintenance windows.", "priority": "High", "metric": "Uptime >= 99.9% (~43 mins downtime/month)"},
            {"id": "NFR-004", "category": "Scalability", "description": "The system architecture shall auto-scale to accommodate a 300% surge during peak lunch/dinner hours.", "priority": "Medium", "metric": "Horizontal scaling within 3 minutes of >75% CPU load"},
            {"id": "NFR-005", "category": "Usability", "description": "The system checkout flow shall be completable in 3 or fewer clicks from cart review.", "priority": "Medium", "metric": "<= 3 interaction steps to place order"}
        ],
        "actors": [
            {"name": "Customer", "role": "End user purchasing food", "responsibilities": "Browses menus, places orders, makes payments, tracks delivery, and provides ratings."},
            {"name": "Restaurant Manager", "role": "Merchant partner", "responsibilities": "Manages restaurant profile, updates menus, confirms orders, and marks food ready for pickup."},
            {"name": "Delivery Partner", "role": "Logistics fulfillment agent", "responsibilities": "Accepts delivery requests, picks up orders from restaurant, and navigates to customer."},
            {"name": "System Administrator", "role": "Platform supervisor", "responsibilities": "Monitors platform health, manages user/restaurant access, resolves disputes, and views financials."}
        ],
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Place Food Order",
                "primary_actor": "Customer",
                "description": "Customer selects food items, reviews cart, submits payment, and initiates delivery.",
                "preconditions": "Customer is authenticated and has added at least one item to cart.",
                "postconditions": "Order record created, payment authorized, notification sent to restaurant.",
                "main_flow": [
                    "Step 1: Customer navigates to checkout screen.",
                    "Step 2: System displays itemized bill with taxes and delivery fee.",
                    "Step 3: Customer selects delivery address and payment method.",
                    "Step 4: System processes transaction via Payment Gateway.",
                    "Step 5: System confirms order and displays real-time tracking interface."
                ]
            },
            {
                "id": "UC-002",
                "title": "Update Menu Inventory",
                "primary_actor": "Restaurant Manager",
                "description": "Restaurant manager updates availability of dishes.",
                "preconditions": "Restaurant manager is logged into restaurant dashboard.",
                "postconditions": "Catalog reflects updated menu availability instantly.",
                "main_flow": [
                    "Step 1: Manager accesses Menu Management tab.",
                    "Step 2: Manager toggles 'Sold Out' switch on specific dishes.",
                    "Step 3: System updates cache and persists new state."
                ]
            },
            {
                "id": "UC-003",
                "title": "Track Order Delivery",
                "primary_actor": "Customer",
                "description": "Customer views live GPS coordinates and estimated arrival time.",
                "preconditions": "Order is accepted and assigned to a delivery partner.",
                "postconditions": "Live map rendered with ETA updates.",
                "main_flow": [
                    "Step 1: Customer opens active order details.",
                    "Step 2: System streams delivery partner GPS location via WebSockets.",
                    "Step 3: Map renders route and updates ETA dynamically."
                ]
            }
        ],
        "business_rules": [
            {"id": "BR-001", "rule": "Orders cannot be canceled after the restaurant has marked the preparation status as 'In Progress'.", "rationale": "Prevents food wastage and financial loss for merchants."},
            {"id": "BR-002", "rule": "A minimum order amount of $5.00 is required for home delivery.", "rationale": "Ensures delivery partner compensation and unit economic feasibility."}
        ],
        "constraints": [
            "Must comply with PCI-DSS guidelines for handling credit card transactions.",
            "Delivery tracking requires mobile device GPS permissions enabled.",
            "Backend must deploy on containerized cloud infrastructure (Docker/Kubernetes)."
        ],
        "assumptions": [
            "Customers and delivery partners have active mobile Internet connectivity.",
            "Third-party payment gateways maintain >=99.95% API service availability.",
            "Restaurants possess a tablet or smartphone device to manage incoming tickets."
        ],
        "dependencies": [
            "Stripe / Razorpay Payment Gateway API",
            "Google Maps Geocoding & Directions API",
            "Twilio SMS / SendGrid Email Notification Gateway"
        ],
        "data_requirements": [
            {"entity": "User", "attributes": "user_id, name, email, phone, hashed_password, role, created_at", "description": "Stores credentials and profiles for all user classes."},
            {"entity": "Restaurant", "attributes": "restaurant_id, name, address, lat, lng, cuisine_type, is_active", "description": "Stores merchant establishment details and geolocation."},
            {"entity": "MenuItem", "attributes": "item_id, restaurant_id, name, price, category, is_available", "description": "Individual dish items linked to specific restaurants."},
            {"entity": "Order", "attributes": "order_id, customer_id, restaurant_id, driver_id, total_amount, status, created_at", "description": "Order records with status transitions and monetary amounts."}
        ],
        "external_interfaces": {
            "user_interfaces": "Responsive web portal and mobile app (iOS/Android) with intuitive card-based layout.",
            "hardware_interfaces": "Standard smartphones with GPS receiver and touch input.",
            "software_interfaces": "PostgreSQL database, Redis cache, Payment Gateway API, Google Maps SDK.",
            "communication_interfaces": "HTTPS/TLS for REST endpoints; WSS (WebSockets) for real-time location streaming."
        },
        "security_requirements": [
            {"id": "SEC-001", "description": "Passwords must be hashed using bcrypt or Argon2 with unique salts.", "priority": "High"},
            {"id": "SEC-002", "description": "Role-Based Access Control (RBAC) must restrict admin endpoints from customer access.", "priority": "High"},
            {"id": "SEC-003", "description": "All API endpoints must implement rate limiting to prevent brute-force and DoS attacks.", "priority": "High"}
        ],
        "performance_requirements": [
            {"id": "PERF-001", "metric": "API Response Time", "requirement": "95% of read queries must complete within 200ms."},
            {"id": "PERF-002", "metric": "Concurrent Users", "requirement": "System must sustain 5,000 active concurrent order sessions without degradation."}
        ],
        "potential_risks": [
            {"risk": "GPS inaccuracy during urban delivery routing", "likelihood": "Medium", "impact": "Medium", "mitigation": "Implement map-matching algorithms and customer call-fallback."},
            {"risk": "Payment gateway downtime during peak traffic", "likelihood": "Low", "impact": "High", "mitigation": "Multi-gateway failover routing (e.g., fallback from Stripe to Razorpay)."}
        ],
        "ambiguities": [
            {"original_statement": "Customers can track deliveries.", "problem": "Does not specify whether tracking is real-time GPS coordinates, estimated milestone timestamps, or SMS alerts.", "suggested_improvement": "The system shall display live delivery partner GPS coordinates on an interactive map with ETA refreshed every 10 seconds."},
            {"original_statement": "Admin should manage restaurants, menus and users.", "problem": "The verb 'manage' is vague and does not enumerate specific CRUD operations, approvals, or auditing requirements.", "suggested_improvement": "The system shall provide an admin dashboard to view, approve, suspend, and edit restaurant listings, menu catalogs, and user accounts."}
        ],
        "missing_requirements": [
            {"area": "Order Cancellation & Refunds", "reason": "No policy or mechanism is specified for customer cancellations or failed deliveries.", "recommendation": "Add FR for customer order cancellation within 60 seconds with automated refund processing."},
            {"area": "Ratings & Reviews", "reason": "Feedback loop is crucial for quality assurance in marketplace platforms.", "recommendation": "Add FR allowing customers to rate restaurants and delivery partners from 1 to 5 stars with written reviews."}
        ],
        "conflicting_requirements": [
            {"conflict": "Instant order placement vs. asynchronous payment verification", "resolution": "Hold order in 'Pending Payment' state until webhook confirms gateway authorization, timing out after 10 minutes."}
        ],
        "quality_analysis": {
            "correctness": {"status": "Acceptable", "findings": "Requirements accurately model typical e-commerce food delivery domain processes."},
            "completeness": {"status": "Needs Improvement", "findings": "Missing explicit refund workflows, notifications, and rider dispatch algorithms."},
            "consistency": {"status": "Acceptable", "findings": "No conflicting terminology found; actor roles are clearly segregated."},
            "unambiguity": {"status": "Needs Improvement", "findings": "Terms like 'track deliveries' and 'manage' required formal operational definitions."},
            "verifiability": {"status": "Acceptable", "findings": "Functional requirements have clear success criteria; non-functional metrics are quantifiable."},
            "feasibility": {"status": "Acceptable", "findings": "All proposed features can be built using standard modern web/mobile stacks and existing APIs."},
            "traceability": {"status": "Acceptable", "findings": "All functional requirements map directly to identifiable actors and use cases."}
        },
        "improved_requirements": [
            {
                "original": "Customers can track deliveries.",
                "problem": "'Track' does not specify technology, refresh rate, or UI presentation.",
                "improved": "The system shall provide an interactive map interface updating the delivery partner's GPS location every 10 seconds with dynamic ETA calculation."
            },
            {
                "original": "Admin should manage restaurants, menus and users.",
                "problem": "'Manage' is an ambiguous catch-all verb that leaves permissions and operations undefined.",
                "improved": "The system shall provide role-restricted administrative interfaces to search, activate, suspend, and export audit logs for restaurants, menu items, and customer accounts."
            },
            {
                "original": "The system should be fast.",
                "problem": "'Fast' is subjective and cannot be objectively verified during testing.",
                "improved": "The system shall respond to 95% of catalog browsing requests within 1.5 seconds under a load of 10,000 concurrent users."
            }
        ],
        "traceability_matrix": [
            {"req_id": "FR-001", "requirement": "Customer Registration", "source_statement": "customers can register", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-002", "requirement": "User Authentication", "source_statement": "login", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-003", "requirement": "Browse Restaurants", "source_statement": "browse restaurants", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-004", "requirement": "Cart Management", "source_statement": "add food to cart", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-005", "requirement": "Order Placement", "source_statement": "place orders", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-006", "requirement": "Delivery Tracking", "source_statement": "track deliveries", "type": "Functional", "priority": "Medium", "related_use_case": "UC-003"},
            {"req_id": "FR-007", "requirement": "Restaurant & Menu Management", "source_statement": "Admin should manage restaurants, menus", "type": "Functional", "priority": "High", "related_use_case": "UC-002"},
            {"req_id": "FR-008", "requirement": "User Management", "source_statement": "and users", "type": "Functional", "priority": "Medium", "related_use_case": "UC-002"}
        ]
    },
    "hospital": {
        "system_overview": {
            "system_name": "Integrated Hospital Information & Management System (CarePulse)",
            "summary": "An enterprise clinical management system designed for patient admissions, outpatient appointments, electronic health records (EHR), laboratory diagnostics, and medical billing.",
            "scope": "Covers patient onboarding, doctor scheduling, electronic prescription generation, nurse vitals entry, lab test result publishing, and invoice generation. Complex robotic surgery integrations are out of scope."
        },
        "system_features": [
            {"feature_id": "SF-001", "name": "Patient Registration & EMR", "description": "Creation and lifecycle management of permanent Electronic Medical Records."},
            {"feature_id": "SF-002", "name": "Doctor Scheduling & Consultation", "description": "Appointment booking, calendar management, and digital clinical note writing."},
            {"feature_id": "SF-003", "name": "Nurse Vitals Station", "description": "Entry and continuous recording of temperature, blood pressure, pulse, and SpO2."},
            {"feature_id": "SF-004", "name": "Laboratory Information System (LIS)", "description": "Test order placement, sample tracking, and digital diagnostic report publication."},
            {"feature_id": "SF-005", "name": "Medical Billing & Insurance", "description": "Itemized billing for consultations, procedures, medications, and insurance claims."}
        ],
        "functional_requirements": [
            {"id": "FR-001", "description": "The system shall register new patients with demographic information and generate a unique Patient ID (PID).", "category": "Patient Management", "priority": "High", "rationale": "Establishes a single source of truth for patient history."},
            {"id": "FR-002", "description": "The system shall allow patients and receptionists to schedule, reschedule, and cancel doctor appointments.", "category": "Scheduling", "priority": "High", "rationale": "Avoids scheduling conflicts and optimizes clinic capacity."},
            {"id": "FR-003", "description": "The system shall enable doctors to view complete longitudinal patient medical history and allergies.", "category": "Clinical", "priority": "High", "rationale": "Critical for clinical diagnostic safety and preventing adverse drug interactions."},
            {"id": "FR-004", "description": "The system shall allow authorized doctors to generate digital prescriptions with drug dosage and duration.", "category": "Prescription", "priority": "High", "rationale": "Eliminates legibility errors and maintains digital audit trail."},
            {"id": "FR-005", "description": "The system shall permit nurses to log patient vital signs (BP, Heart Rate, Temp, SpO2) timestamped per shift.", "category": "Nursing", "priority": "High", "rationale": "Enables continuous inpatient clinical monitoring."},
            {"id": "FR-006", "description": "The system shall allow lab technicians to input diagnostic test results and attach PDF reports.", "category": "Laboratory", "priority": "Medium", "rationale": "Provides doctors with immediate diagnostic data."},
            {"id": "FR-007", "description": "The system shall generate itemized hospital bills and process insurance pre-authorization requests.", "category": "Billing", "priority": "High", "rationale": "Ensures accurate financial settlements and compliance."}
        ],
        "non_functional_requirements": [
            {"id": "NFR-001", "category": "Security", "description": "The system shall maintain strict HIPAA/GDPR compliance with end-to-end encryption for protected health information (PHI).", "priority": "High", "metric": "Zero unencrypted PHI in transit or storage; AES-256"},
            {"id": "NFR-002", "category": "Reliability", "description": "The system shall provide 99.99% availability for inpatient and emergency care modules.", "priority": "High", "metric": "Max 4.38 minutes downtime per month"},
            {"id": "NFR-003", "category": "Auditability", "description": "Every access, modification, or export of patient records must be immutably logged with timestamp and user ID.", "priority": "High", "metric": "100% immutable audit log coverage"},
            {"id": "NFR-004", "category": "Performance", "description": "Patient medical record retrieval must complete within 1.0 second during emergency consultations.", "priority": "High", "metric": "Query execution time < 1000ms"}
        ],
        "actors": [
            {"name": "Patient", "role": "Healthcare consumer", "responsibilities": "Registers, books appointments, views lab reports, and pays invoices."},
            {"name": "Doctor", "role": "Medical practitioner", "responsibilities": "Reviews patient history, conducts consultations, writes diagnoses, and orders labs/prescriptions."},
            {"name": "Nurse", "role": "Clinical care provider", "responsibilities": "Records patient vitals, administers medications, and updates inpatient chart notes."},
            {"name": "Lab Technician", "role": "Diagnostic specialist", "responsibilities": "Processes lab samples, enters results, and uploads diagnostic imagery."},
            {"name": "Hospital Administrator", "role": "Operations & Billing lead", "responsibilities": "Manages doctor schedules, oversees billing, audits compliance, and handles user privileges."}
        ],
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Book Outpatient Appointment",
                "primary_actor": "Patient",
                "description": "Patient selects a specialty, doctor, date, and available time slot.",
                "preconditions": "Patient has an active PID.",
                "postconditions": "Appointment booked, calendar reserved, SMS confirmation dispatched.",
                "main_flow": [
                    "Step 1: Patient selects medical specialty and doctor.",
                    "Step 2: System presents available calendar slots.",
                    "Step 3: Patient confirms desired slot and enters chief complaint.",
                    "Step 4: System locks the slot and issues appointment token."
                ]
            },
            {
                "id": "UC-002",
                "title": "Consultation & Prescription Issuance",
                "primary_actor": "Doctor",
                "description": "Doctor examines patient, reviews vitals, and issues electronic prescription.",
                "preconditions": "Patient checked in and vitals recorded by nurse.",
                "postconditions": "Prescription stored in EHR, forwarded to in-house pharmacy.",
                "main_flow": [
                    "Step 1: Doctor opens patient EHR record.",
                    "Step 2: Doctor reviews nurse-recorded vitals.",
                    "Step 3: Doctor selects medications and sets dosage/frequency.",
                    "Step 4: System performs drug-allergy contraindication check.",
                    "Step 5: Doctor signs and finalizes prescription."
                ]
            }
        ],
        "business_rules": [
            {"id": "BR-001", "rule": "Prescriptions cannot be finalized without a documented primary diagnosis ICD-10 code.", "rationale": "Prevents improper medication dispensing and satisfies insurance requirements."},
            {"id": "BR-002", "rule": "Only licensed physicians can authorize controlled substance prescriptions.", "rationale": "Legal compliance with medical regulatory boards."}
        ],
        "constraints": [
            "Mandatory compliance with HIPAA, HITECH, and local health data sovereignty laws.",
            "Must integrate with DICOM standard for medical imaging (X-rays, CT scans)."
        ],
        "assumptions": [
            "Hospital local area network (LAN) provides high-bandwidth redundancy across all clinical wards.",
            "Doctors and nurses are trained on basic digital medical record interfaces."
        ],
        "dependencies": [
            "HL7 / FHIR clinical data interoperability standard",
            "National Drug Code (NDC) database for medication lookup",
            "Insurance TPA clearinghouse gateway"
        ],
        "data_requirements": [
            {"entity": "Patient", "attributes": "pid, first_name, last_name, dob, gender, blood_group, allergies, contact", "description": "Core patient demographic and clinical baseline."},
            {"entity": "MedicalRecord", "attributes": "record_id, pid, doctor_id, diagnosis, clinical_notes, created_at", "description": "Consultation records containing notes and diagnostic codes."},
            {"entity": "VitalsLog", "attributes": "log_id, pid, nurse_id, systolic_bp, diastolic_bp, pulse, temp, spo2, timestamp", "description": "Timestamped physiological measurements."},
            {"entity": "Invoice", "attributes": "invoice_id, pid, total_due, insurance_covered, patient_payable, status", "description": "Itemized clinical billing charges."}
        ],
        "external_interfaces": {
            "user_interfaces": "Web-based clinical workstation UI optimized for tablets and desktop monitors.",
            "hardware_interfaces": "Barcode scanners for patient wristbands; networked vital signs monitors.",
            "software_interfaces": "HL7/FHIR interfaces, LIS analyzers, PACS imaging servers.",
            "communication_interfaces": "Encrypted HTTPS/WSS, DICOM protocol over TCP/IP."
        },
        "security_requirements": [
            {"id": "SEC-001", "description": "Enforce Multi-Factor Authentication (MFA) for all clinical and administrative staff.", "priority": "High"},
            {"id": "SEC-002", "description": "Implement automated session lock after 3 minutes of terminal inactivity.", "priority": "High"}
        ],
        "performance_requirements": [
            {"id": "PERF-001", "metric": "Emergency Record Access", "requirement": "EHR records must load within 1.0 second upon scanning patient wristband."},
            {"id": "PERF-002", "metric": "Report Generation", "requirement": "Consolidated lab summary PDFs must render in less than 3 seconds."}
        ],
        "potential_risks": [
            {"risk": "Data breach of protected health information (PHI)", "likelihood": "Low", "impact": "Critical", "mitigation": "Field-level database encryption and strict role-based access audits."},
            {"risk": "Incorrect medication dosage entry", "likelihood": "Medium", "impact": "High", "mitigation": "Automated dosage range validators and contraindication warning popups."}
        ],
        "ambiguities": [
            {"original_statement": "medical records management", "problem": "Does not specify whether records include structured data, unstructured physician notes, or DICOM imaging.", "suggested_improvement": "The system shall store structured EMR data (diagnoses, vitals, prescriptions) and attach binary medical records (PDFs, DICOM images) up to 50MB per file."},
            {"original_statement": "Nurses record vitals.", "problem": "Does not enumerate which physiological parameters are tracked or alert thresholds.", "suggested_improvement": "The system shall record temperature, heart rate, blood pressure, and SpO2, triggering visual alerts if values exceed predefined clinical thresholds."}
        ],
        "missing_requirements": [
            {"area": "Emergency Triage & Bed Management", "reason": "Hospitals require active bed occupancy tracking and emergency ward prioritization.", "recommendation": "Add FR for inpatient bed allocation and real-time ward occupancy dashboards."},
            {"area": "Pharmacy Dispensing", "reason": "Prescriptions must be fulfilled by pharmacists with inventory deduction.", "recommendation": "Add FR for pharmacy stock deduction upon dispensing verified medication."}
        ],
        "conflicting_requirements": [
            {"conflict": "Immediate emergency access vs. strict multi-factor authentication", "resolution": "Implement a supervised 'Break-Glass' emergency override with mandatory incident logging."}
        ],
        "quality_analysis": {
            "correctness": {"status": "Acceptable", "findings": "Clinical workflow sequence aligns with hospital operational standards."},
            "completeness": {"status": "Needs Improvement", "findings": "Needs explicit bed management, emergency triage, and pharmacy stock modules."},
            "consistency": {"status": "Acceptable", "findings": "Consistent terminology used for patient records and practitioner roles."},
            "unambiguity": {"status": "Needs Improvement", "findings": "Broad terms like 'vitals' and 'records' require explicit parameter enumerations."},
            "verifiability": {"status": "Acceptable", "findings": "Requirements can be formally tested against clinical test scenarios."},
            "feasibility": {"status": "Acceptable", "findings": "Standard hospital information systems routinely implement these modules."},
            "traceability": {"status": "Acceptable", "findings": "Each requirement maps to designated clinical and administrative actors."}
        },
        "improved_requirements": [
            {
                "original": "Nurses record vitals.",
                "problem": "Vague on specific physiological parameters and frequency.",
                "improved": "The system shall provide a dedicated nurse portal to record systolic/diastolic blood pressure, pulse rate, body temperature, and oxygen saturation (SpO2) with automated abnormal threshold warnings."
            },
            {
                "original": "Doctors can view patient history and prescribe medications.",
                "problem": "Lacks contraindication checking and structured prescription format.",
                "improved": "The system shall display chronological patient medical history, allergies, and allow doctors to issue electronic prescriptions verified against an automated drug-interaction database."
            }
        ],
        "traceability_matrix": [
            {"req_id": "FR-001", "requirement": "Patient Registration", "source_statement": "patient registration", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-002", "requirement": "Appointment Scheduling", "source_statement": "appointment scheduling with doctors", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-003", "requirement": "Medical Records Management", "source_statement": "medical records management", "type": "Functional", "priority": "High", "related_use_case": "UC-002"},
            {"req_id": "FR-004", "requirement": "Prescription Issuance", "source_statement": "prescribe medications", "type": "Functional", "priority": "High", "related_use_case": "UC-002"},
            {"req_id": "FR-005", "requirement": "Vitals Recording", "source_statement": "Nurses record vitals", "type": "Functional", "priority": "High", "related_use_case": "UC-002"},
            {"req_id": "FR-006", "requirement": "Laboratory Diagnostics", "source_statement": "laboratory test results", "type": "Functional", "priority": "Medium", "related_use_case": "UC-002"},
            {"req_id": "FR-007", "requirement": "Billing & Invoicing", "source_statement": "and billing", "type": "Functional", "priority": "High", "related_use_case": "UC-001"}
        ]
    },
    "smart_campus": {
        "system_overview": {
            "system_name": "Smart Campus & Academic Resource Portal (EduSphere)",
            "summary": "An integrated higher-education institutional portal supporting course enrollment, biometric attendance tracking, digital gradebook management, and a centralized library catalog.",
            "scope": "Covers student portals, faculty attendance logging, grade publishing, book checkout/reservations, and overdue fine management. Campus dining card balance is out of scope."
        },
        "system_features": [
            {"feature_id": "SF-001", "name": "Academic Profile & Schedule", "description": "Student course timetables, enrolled subjects, and credit requirements."},
            {"feature_id": "SF-002", "name": "Attendance Tracking", "description": "Daily lecture attendance capture with automated low-attendance warnings."},
            {"feature_id": "SF-003", "name": "Assessment & Gradebook", "description": "Faculty assignment uploads, student submissions, and grade publication."},
            {"feature_id": "SF-004", "name": "Library Management System", "description": "Book catalog search, checkout, renewal, and automated fine calculation."}
        ],
        "functional_requirements": [
            {"id": "FR-001", "description": "The system shall display personalized course schedules and exam timetables for enrolled students.", "category": "Academic", "priority": "High", "rationale": "Keeps students informed of daily academic commitments."},
            {"id": "FR-002", "description": "The system shall allow faculty to record attendance per lecture session and calculate aggregate percentages.", "category": "Attendance", "priority": "High", "rationale": "Enforces institutional attendance thresholds."},
            {"id": "FR-003", "description": "The system shall alert students and advisors if attendance drops below 75% in any registered course.", "category": "Attendance", "priority": "Medium", "rationale": "Prevents exam debarment through early notification."},
            {"id": "FR-004", "description": "The system shall allow faculty to create assignments, define deadlines, and grade submitted student work.", "category": "Grading", "priority": "High", "rationale": "Facilitates continuous academic evaluation."},
            {"id": "FR-005", "description": "The system shall allow students to search the university library OPAC catalog and reserve available books.", "category": "Library", "priority": "Medium", "rationale": "Streamlines access to educational literature."},
            {"id": "FR-006", "description": "The system shall compute overdue book fines at a rate of $0.50/day and block checkout for balances > $10.00.", "category": "Library", "priority": "Medium", "rationale": "Encourages prompt return of shared university assets."}
        ],
        "non_functional_requirements": [
            {"id": "NFR-001", "category": "Performance", "description": "The portal shall sustain 8,000 concurrent student logins within 10 minutes during grade release windows.", "priority": "High", "metric": "P99 latency < 2000ms under 8k concurrent users"},
            {"id": "NFR-002", "category": "Security", "description": "Grade modification endpoints must be protected with audit trails and IP-restricted faculty access.", "priority": "High", "metric": "100% grade edit logging"},
            {"id": "NFR-003", "category": "Availability", "description": "The portal shall be accessible 99.5% of the time throughout active academic semesters.", "priority": "High", "metric": "Uptime >= 99.5%"}
        ],
        "actors": [
            {"name": "Student", "role": "Undergraduate/Postgraduate learner", "responsibilities": "Views schedule, checks attendance, submits assignments, views grades, borrows books."},
            {"name": "Faculty", "role": "Academic instructor", "responsibilities": "Marks attendance, posts course syllabus, creates assignments, inputs exam scores."},
            {"name": "Librarian", "role": "Resource manager", "responsibilities": "Catalogs books, processes checkout/returns, manages overdue fines."},
            {"name": "Dean / Academic Admin", "role": "Institutional supervisor", "responsibilities": "Oversees department performance, audits attendance, resolves grade disputes."}
        ],
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Mark Lecture Attendance",
                "primary_actor": "Faculty",
                "description": "Faculty selects course section and marks student presence or absence.",
                "preconditions": "Faculty is assigned to course session.",
                "postconditions": "Attendance persisted, percentages recalculated.",
                "main_flow": [
                    "Step 1: Faculty selects course and current date/period.",
                    "Step 2: System displays registered student roster.",
                    "Step 3: Faculty marks absences and submits roster.",
                    "Step 4: System updates student records and sends alert if threshold breached."
                ]
            },
            {
                "id": "UC-002",
                "title": "Borrow Library Book",
                "primary_actor": "Student",
                "description": "Student scans library book barcode for 14-day checkout.",
                "preconditions": "Student has no outstanding overdue fines exceeding $10.",
                "postconditions": "Book status set to Borrowed; due date assigned.",
                "main_flow": [
                    "Step 1: Student presents student ID and book barcode to librarian/kiosk.",
                    "Step 2: System verifies active enrollment and fine balance.",
                    "Step 3: System records loan with 14-day due date.",
                    "Step 4: Due date receipt emailed to student."
                ]
            }
        ],
        "business_rules": [
            {"id": "BR-001", "rule": "Students with attendance below 75% cannot download exam hall tickets.", "rationale": "Institutional academic eligibility rule."},
            {"id": "BR-002", "rule": "Maximum of 3 books can be borrowed simultaneously by an undergraduate student.", "rationale": "Fair distribution of library resources."}
        ],
        "constraints": [
            "Must integrate with university Active Directory (LDAP) for single sign-on.",
            "Must support mobile responsive layout for smartphone student usage."
        ],
        "assumptions": [
            "Students have registered university email addresses for notification delivery.",
            "Library books are tagged with standardized ISBN barcodes."
        ],
        "dependencies": [
            "University LDAP / OAuth2 Single Sign-On",
            "SMTP Server for academic notification emails"
        ],
        "data_requirements": [
            {"entity": "Student", "attributes": "student_id, roll_number, name, program, semester, email", "description": "Student academic identity and enrollment state."},
            {"entity": "AttendanceRecord", "attributes": "record_id, course_id, student_id, date, status, faculty_id", "description": "Lecture-level presence/absence log."},
            {"entity": "Assignment", "attributes": "assignment_id, course_id, title, max_marks, due_date", "description": "Course evaluation tasks."},
            {"entity": "BookLoan", "attributes": "loan_id, book_id, student_id, issue_date, due_date, return_date, fine_amount", "description": "Library asset circulation records."}
        ],
        "external_interfaces": {
            "user_interfaces": "Modern responsive portal with dashboard views for students and faculty.",
            "hardware_interfaces": "Barcode/RFID scanners at library circulation desks.",
            "software_interfaces": "University LDAP, PostgreSQL DB, Canvas/Moodle LMS connectors.",
            "communication_interfaces": "HTTPS/TLS REST APIs."
        },
        "security_requirements": [
            {"id": "SEC-001", "description": "Single Sign-On (SSO) integration via SAML 2.0 or OAuth 2.0.", "priority": "High"},
            {"id": "SEC-002", "description": "Role-based authorization preventing students from editing attendance or grades.", "priority": "High"}
        ],
        "performance_requirements": [
            {"id": "PERF-001", "metric": "Grade Release Load", "requirement": "Serve 8,000 concurrent page requests within 2 seconds."},
            {"id": "PERF-002", "metric": "Search Latency", "requirement": "Library OPAC book search returns in < 500ms for 50,000 titles."}
        ],
        "potential_risks": [
            {"risk": "Server crash during simultaneous grade release", "likelihood": "Medium", "impact": "High", "mitigation": "Read-replica database scaling and static grade caching via CDN."}
        ],
        "ambiguities": [
            {"original_statement": "track attendance", "problem": "Does not specify whether attendance is recorded manually, via RFID, or biometric scans.", "suggested_improvement": "The system shall allow faculty to record lecture attendance via a digital roster, with optional RFID smartcard integration."},
            {"original_statement": "check grades", "problem": "Does not specify whether grades are final GPA, letter grades, or raw assignment marks.", "suggested_improvement": "The system shall display both raw continuous assessment marks and weighted semester letter grades (A-F) with GPA computation."}
        ],
        "missing_requirements": [
            {"area": "Fee Payment Portal", "reason": "Tuition and semester fee payment is fundamental to student enrollment.", "recommendation": "Add FR for student tuition fee installment payments with digital receipts."},
            {"area": "Course Feedback & Evaluation", "reason": "Universities require end-of-term instructor evaluations.", "recommendation": "Add FR allowing students to submit anonymous course feedback."}
        ],
        "conflicting_requirements": [
            {"conflict": "Grade visibility immediately upon faculty submission vs. department head review", "resolution": "Maintain grades in 'Draft' status until approved by Department Chair, after which they are published."}
        ],
        "quality_analysis": {
            "correctness": {"status": "Acceptable", "findings": "Covers primary university student information system operations accurately."},
            "completeness": {"status": "Needs Improvement", "findings": "Missing tuition fee processing and course registration drop/add periods."},
            "consistency": {"status": "Acceptable", "findings": "Academic terminology and role delineations are consistent."},
            "unambiguity": {"status": "Needs Improvement", "findings": "Broad terms like 'check grades' and 'track attendance' require specific definitions."},
            "verifiability": {"status": "Acceptable", "findings": "Grading rules and attendance thresholds are numerically quantifiable."},
            "feasibility": {"status": "Acceptable", "findings": "Can be developed readily using standard web frameworks and relational databases."},
            "traceability": {"status": "Acceptable", "findings": "Direct mapping between actors (Student, Faculty, Librarian) and requirements."}
        },
        "improved_requirements": [
            {
                "original": "Faculty can post assignments and mark attendance.",
                "problem": "Combines two distinct functional modules without acceptance rules.",
                "improved": "The system shall provide faculty with an assignment management module (supporting file attachments up to 25MB) and a separate digital attendance register with 75% threshold alerting."
            },
            {
                "original": "Librarian manages book inventory, issues, and overdue fines.",
                "problem": "'Manages' does not define specific fine calculation rules or loan periods.",
                "improved": "The system shall provide a library circulation module allowing librarians to issue books for 14 days, process returns, and automatically compute overdue fines at $0.50 per day."
            }
        ],
        "traceability_matrix": [
            {"req_id": "FR-001", "requirement": "Course Schedule Display", "source_statement": "view course schedules", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-002", "requirement": "Attendance Recording", "source_statement": "track attendance / mark attendance", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-003", "requirement": "Attendance Warning", "source_statement": "track attendance", "type": "Functional", "priority": "Medium", "related_use_case": "UC-001"},
            {"req_id": "FR-004", "requirement": "Assignments & Grading", "source_statement": "post assignments and check grades", "type": "Functional", "priority": "High", "related_use_case": "UC-001"},
            {"req_id": "FR-005", "requirement": "Library Book Search & Issue", "source_statement": "borrow library books / issues", "type": "Functional", "priority": "Medium", "related_use_case": "UC-002"},
            {"req_id": "FR-006", "requirement": "Overdue Fine Calculation", "source_statement": "overdue fines", "type": "Functional", "priority": "Medium", "related_use_case": "UC-002"}
        ]
    }
}


class RequirementAnalyzer:
    """
    Main requirements engineering analyzer agent.
    Coordinates LLM queries, JSON schema enforcement, and fallback parsing.
    """

    def __init__(self, default_model: str = "gpt-4o-mini"):
        self.default_model = os.getenv("MODEL_NAME", default_model)

    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """
        Safely extracts and parses JSON from LLM output, handling markdown code blocks
        and potential preamble or postamble.
        """
        text = text.strip()

        # Handle ```json ... ``` or ``` ... ```
        json_block_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.DOTALL)
        if json_block_match:
            candidate = json_block_match.group(1)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Handle raw JSON starting from first '{' to last '}'
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidate = text[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # Try cleaning trailing commas
                cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    pass

        # Final direct attempt
        return json.loads(text)

    def _match_demo_dataset(self, text: str) -> Dict[str, Any]:
        """Matches raw input to the best matching pre-analyzed demo dataset."""
        text_lower = text.lower()
        if "food" in text_lower or "delivery" in text_lower or "restaurant" in text_lower:
            return DEMO_DATASETS["food_delivery"]
        elif "hospital" in text_lower or "patient" in text_lower or "doctor" in text_lower or "nurse" in text_lower:
            return DEMO_DATASETS["hospital"]
        elif "campus" in text_lower or "student" in text_lower or "library" in text_lower or "college" in text_lower:
            return DEMO_DATASETS["smart_campus"]
        # Default to food delivery if ambiguous
        return DEMO_DATASETS["food_delivery"]

    def analyze(
        self,
        raw_requirements: str,
        api_key: str = "",
        base_url: str = "",
        model_name: str = "",
        demo_mode: bool = False
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Executes requirement analysis on the raw text.

        Returns:
            Tuple[bool, Dict[str, Any], str]: (success, analysis_data_dict, message)
        """
        if not raw_requirements or not raw_requirements.strip():
            return False, {}, "❌ Error: Requirement input cannot be empty. Please enter or select a sample requirement."

        # Resolve API key (Groq or OpenAI)
        effective_key = (api_key or os.getenv("GROQ_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")).strip()
        effective_base_url = (base_url or os.getenv("GROQ_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", "")).strip()
        
        # Auto-configure base URL for Groq if key is a Groq key (starts with gsk_ or GROQ_API_KEY is set)
        is_groq = effective_key.startswith("gsk_") or bool(os.getenv("GROQ_API_KEY"))
        if is_groq and not effective_base_url:
            effective_base_url = "https://api.groq.com/openai/v1"

        default_model = "llama-3.3-70b-versatile" if is_groq else "gpt-4o-mini"
        effective_model = (model_name or os.getenv("MODEL_NAME", "")).strip() or default_model

        if demo_mode or not effective_key:
            demo_data = self._match_demo_dataset(raw_requirements)
            validated = validate_analysis_data(demo_data)
            mode_note = "⚡ [Viva Demo Mode] Analyzed using offline requirements engineering dataset. (No API key consumed)."
            if not effective_key and not demo_mode:
                mode_note = "ℹ️ Notice: No API key detected. Loaded offline requirements engineering dataset for demo."
            return True, validated, mode_note

        # Live LLM API execution
        try:
            from openai import OpenAI
            client_kwargs = {"api_key": effective_key}
            if effective_base_url:
                client_kwargs["base_url"] = effective_base_url

            client = OpenAI(**client_kwargs)

            prompt = ANALYSIS_USER_PROMPT.format(raw_requirements=raw_requirements.strip())

            # Enable json_object response format for supported models (OpenAI or Groq json-supported models)
            extra_kwargs = {}
            if "gpt-" in effective_model or "llama" in effective_model or "mixtral" in effective_model:
                extra_kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(
                model=effective_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                **extra_kwargs
            )

            raw_reply = response.choices[0].message.content or ""
            parsed_data = self._extract_json_from_response(raw_reply)
            validated = validate_analysis_data(parsed_data)
            return True, validated, f"✅ Successfully analyzed requirements using model `{effective_model}`."

        except Exception as e:
            err_msg = str(e)
            # Provide friendly explanations for common errors
            if "AuthenticationError" in err_msg or "401" in err_msg:
                user_msg = "❌ Authentication Error: Invalid API key provided. Please check your key in the Settings accordion or .env file."
            elif "RateLimitError" in err_msg or "429" in err_msg:
                user_msg = "❌ Rate Limit Exceeded: Your LLM API quota or rate limit has been reached. You can switch to 'Viva Demo Mode' for offline presentation."
            elif "APIConnectionError" in err_msg or "ConnectionError" in err_msg:
                user_msg = "❌ Network Error: Could not connect to LLM endpoint. Check your internet connection or use 'Viva Demo Mode'."
            elif isinstance(e, json.JSONDecodeError):
                user_msg = "❌ Parsing Error: LLM response could not be parsed into valid JSON. Please try again or switch to Demo Mode."
            else:
                user_msg = f"❌ Analysis Failed: {err_msg}"

            return False, {}, user_msg
