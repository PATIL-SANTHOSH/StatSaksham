import os
import sys
import random
from datetime import date, datetime, timedelta, timezone

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal, engine, Base
from app.core.security import get_password_hash
import app.models  # Register all 18+ models & 20 tables with SQLAlchemy metadata
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.competency import Competency, CompetencyRequirement, EmployeeCompetency
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResult
from app.models.course import IGOTCourse, NSSTAProgramme
from app.models.progress import LearningProgress
from app.models.recommendation import Recommendation
from app.models.quiz import QuizDocument, QuizChunk, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.ai_conversation import AIConversation, AIMessage
from app.services.recommendation_service import RecommendationService

def seed_database():
    print("Starting database seeding for STATSAKSHAM (SIH26101)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    demo_pass_hash = get_password_hash("demo123")
    admin_pass_hash = get_password_hash("admin123")

    # -------------------------------------------------------------
    # 1. DEPARTMENTS / DIVISIONS (MoSPI)
    # -------------------------------------------------------------
    departments_data = [
        {"code": "NAD", "name": "National Accounts Division", "head": "Additional Director General", "desc": "Compilation of GDP, GVA, and National Accounts Aggregates"},
        {"code": "PSD", "name": "Price Statistics Division", "head": "Deputy Director General", "desc": "Compilation and release of Consumer Price Index (CPI) and IIP"},
        {"code": "FOD", "name": "Field Operations Division", "head": "Additional Director General", "desc": "Nationwide primary field survey operations for NSS and PLFS"},
        {"code": "SDRD", "name": "Survey Design & Research Division", "head": "Deputy Director General", "desc": "Statistical sampling design, survey frames, and schedules"},
        {"code": "SSD", "name": "Social Statistics Division", "head": "Deputy Director General", "desc": "SDG National Indicator Framework, Gender and Social Indicators"},
        {"code": "ESD", "name": "Economic Statistics Division", "head": "Deputy Director General", "desc": "Annual Survey of Industries (ASI), Economic Census, and Index of Services"},
        {"code": "DIID", "name": "Data Informatics & Innovation Division", "head": "Additional Director General", "desc": "IT infrastructure, Big Data, AI analytics, and Open Data portals"},
        {"code": "CPD", "name": "Coordination and Publication Division", "head": "Deputy Director General", "desc": "Statistical publications, international coordination, and standards"}
    ]

    for d in departments_data:
        dept = Department(code=d["code"], name=d["name"], description=d["desc"], head_designation=d["head"])
        db.add(dept)
    db.commit()
    print(f"[OK] Seeded {len(departments_data)} MoSPI divisions.")

    # -------------------------------------------------------------
    # 2. COMPETENCIES (26 across 4 categories)
    # -------------------------------------------------------------
    competencies_data = [
        # A. STATISTICAL
        {"code": "STAT_SURVEY", "name": "Survey Design", "category": "Statistical", "domain": "Survey & Sampling", "desc": "Schedules, questionnaire design, multi-stage stratification and pilot testing."},
        {"code": "STAT_SAMPLING", "name": "Sampling Techniques", "category": "Statistical", "domain": "Survey & Sampling", "desc": "Stratified sampling, cluster sampling, PPS, FSU selection, and multiplier calculations."},
        {"code": "STAT_NAT_ACC", "name": "National Accounts", "category": "Statistical", "domain": "Macroeconomic Statistics", "desc": "System of National Accounts (SNA 2008), GDP estimation, GVA, and supply-use tables."},
        {"code": "STAT_PRICE", "name": "Price Statistics", "category": "Statistical", "domain": "Macroeconomic Statistics", "desc": "CPI Rural/Urban/Combined, WPI indices, Laspeyres/Paasche formula, and price collection."},
        {"code": "STAT_LABOUR", "name": "Labour Statistics", "category": "Statistical", "domain": "Socio-Economic Statistics", "desc": "Periodic Labour Force Survey (PLFS), LFPR, WPR, and unemployment rates."},
        {"code": "STAT_AGRI", "name": "Agricultural Statistics", "category": "Statistical", "domain": "Sectoral Statistics", "desc": "Crop estimation surveys, land use statistics, and agricultural input cost indices."},
        {"code": "STAT_IND", "name": "Industrial Statistics", "category": "Statistical", "domain": "Sectoral Statistics", "desc": "Annual Survey of Industries (ASI), Index of Industrial Production (IIP), and NIC codes."},
        {"code": "STAT_SDG", "name": "SDG Indicators", "category": "Statistical", "domain": "Global & National Frameworks", "desc": "National Indicator Framework (NIF) for 17 Sustainable Development Goals."},
        {"code": "STAT_META", "name": "Metadata Standards", "category": "Statistical", "domain": "Data Governance", "desc": "SDMX standards, National Metadata Repository, and data classification schemas."},
        {"code": "STAT_QUALITY", "name": "Data Quality Frameworks", "category": "Statistical", "domain": "Quality Assurance", "desc": "NQAF guidelines, survey validation, error auditing, and imputation techniques."},

        # B. TECHNICAL
        {"code": "TECH_PYTHON", "name": "Python for Data Analysis", "category": "Technical", "domain": "Computing & Scripting", "desc": "Pandas, NumPy, automated ETL pipelines, and survey microdata processing."},
        {"code": "TECH_R", "name": "R Programming", "category": "Technical", "domain": "Computing & Scripting", "desc": "Survey package in R, econometric modeling, time-series, and ggplot2 visualizations."},
        {"code": "TECH_SQL", "name": "SQL & Database Queries", "category": "Technical", "domain": "Database Management", "desc": "Relational query design, indexing, large dataset joins, and PostgreSQL/Oracle."},
        {"code": "TECH_STATA", "name": "Stata Econometrics", "category": "Technical", "domain": "Statistical Software", "desc": "Panel data regression, instrumental variables, and survey weighting analysis."},
        {"code": "TECH_SPSS", "name": "SPSS Statistics", "category": "Technical", "domain": "Statistical Software", "desc": "Descriptive statistics, ANOVA, cross-tabulations, and factor analysis."},
        {"code": "TECH_SAS", "name": "SAS Analytics", "category": "Technical", "domain": "Statistical Software", "desc": "Enterprise SAS programming, macro development, and large batch transformations."},
        {"code": "TECH_GIS", "name": "GIS & Spatial Statistics", "category": "Technical", "domain": "Geospatial", "desc": "QGIS, spatial autocorrelation, choropleth mapping, and Urban Frame Survey digitization."},
        {"code": "TECH_DATAVIZ", "name": "Data Visualization & Dashboards", "category": "Technical", "domain": "Analytics & Reporting", "desc": "Power BI, Tableau, interactive web charts, and official statistical infographics."},
        {"code": "TECH_AIML", "name": "AI & Machine Learning in Statistics", "category": "Technical", "domain": "Emerging Technologies", "desc": "Automated data validation, predictive imputation, NLP for occupation classification."},
        {"code": "TECH_CLOUD", "name": "Cloud Computing for Government", "category": "Technical", "domain": "Infrastructure", "desc": "Government Community Cloud (GCC), containerized statistical workflows."},
        {"code": "TECH_APIS", "name": "APIs & Data Integration", "category": "Technical", "domain": "Interoperability", "desc": "REST APIs, Open API specifications, automated microdata exchange protocols."},
        {"code": "TECH_OPENDATA", "name": "Open Data Standards", "category": "Technical", "domain": "Dissemination", "desc": "Data.gov.in publishing standards, machine-readable formats (JSON/CSV), FAIR principles."},

        # C. DIGITAL GOVERNANCE
        {"code": "GOV_CYBER", "name": "Cybersecurity & Data Protection", "category": "Digital Governance", "domain": "Security & Compliance", "desc": "CERT-In guidelines, server hardening, role-based access, and secure data storage."},
        {"code": "GOV_PRIVACY", "name": "Data Privacy & Anonymization", "category": "Digital Governance", "domain": "Compliance", "desc": "DPDP Act compliance, k-anonymity, differential privacy, and microdata de-identification."},
        {"code": "GOV_DPI", "name": "Digital Public Infrastructure", "category": "Digital Governance", "domain": "Governance", "desc": "India Stack, Aadhaar e-Sign, DigiLocker integration, and public digital platforms."},

        # D. BEHAVIOURAL / MANAGERIAL
        {"code": "BEH_LEAD", "name": "Leadership & Team Management", "category": "Behavioural / Managerial", "domain": "Management", "desc": "Field team supervision, conflict resolution, and capacity building."},
        {"code": "BEH_COMM", "name": "Official Communication & Reporting", "category": "Behavioural / Managerial", "domain": "Communication", "desc": "Statistical report drafting, executive briefs, parliamentary replies, and dissemination."},
        {"code": "BEH_ETHICS", "name": "Public Service Ethics & Integrity", "category": "Behavioural / Managerial", "domain": "Ethics", "desc": "Code of Conduct, objectivity in official statistics, and confidentiality mandates."}
    ]

    comp_map = {}
    for c in competencies_data:
        comp = Competency(
            code=c["code"],
            name=c["name"],
            category=c["category"],
            domain=c["domain"],
            description=c["desc"],
            max_level=5
        )
        db.add(comp)
        db.flush()
        comp_map[c["code"]] = comp.id
    db.commit()
    print(f"[OK] Seeded {len(competencies_data)} competencies.")

    # -------------------------------------------------------------
    # 3. ROLE COMPETENCY REQUIREMENTS
    # -------------------------------------------------------------
    role_requirements_data = {
        "Statistical Data Analyst": [
            ("TECH_PYTHON", 4, 5, "Core daily tool for automated data cleaning, pipeline scripts, and statistical modeling."),
            ("TECH_SQL", 4, 4, "Essential for querying complex relational survey databases and microdata archives."),
            ("STAT_NAT_ACC", 4, 4, "Required for macroeconomic aggregation and GVA calculation."),
            ("TECH_DATAVIZ", 4, 4, "Key for building interactive dashboards and executive reports."),
            ("STAT_SAMPLING", 3, 3, "Needed to understand weighting and variance estimation in survey analysis."),
            ("STAT_QUALITY", 4, 4, "Vital for validation rules and automated error imputation."),
            ("GOV_CYBER", 3, 3, "Ensures statistical microdata is stored and processed securely.")
        ],
        "Price Index Statistician": [
            ("STAT_PRICE", 5, 5, "Critical core requirement for CPI, WPI, and index number compilation."),
            ("TECH_SQL", 4, 4, "Essential for price quote database management and anomaly detection."),
            ("TECH_PYTHON", 3, 3, "Used for automating index calculation runs and outlier diagnostics."),
            ("STAT_QUALITY", 4, 4, "Mandatory for outlier validation and price quote imputation."),
            ("TECH_DATAVIZ", 3, 3, "Needed for monthly price bulletin charts and trend infographics."),
            ("BEH_COMM", 3, 3, "Important for drafting monthly inflation press releases.")
        ],
        "Survey Operations Specialist": [
            ("STAT_SURVEY", 5, 5, "Primary requirement for designing schedules and survey workflows."),
            ("STAT_SAMPLING", 5, 5, "Fundamental for drawing representative samples and calculating multipliers."),
            ("STAT_LABOUR", 4, 4, "Required for PLFS survey operations and activity classification."),
            ("BEH_LEAD", 4, 4, "Crucial for leading regional survey teams and enumerators."),
            ("TECH_GIS", 3, 3, "Needed for Urban Frame Survey map digitization and block verification."),
            ("GOV_PRIVACY", 4, 4, "Ensures respondent confidentiality under statistical privacy guidelines.")
        ],
        "Research Officer": [
            ("TECH_PYTHON", 4, 4, "Key for statistical machine learning, predictive modeling, and data science."),
            ("TECH_R", 4, 4, "Used for econometric testing and survey analysis packages."),
            ("TECH_AIML", 4, 4, "Required for exploring AI applications in official statistical automation."),
            ("STAT_SDG", 4, 4, "Vital for monitoring national indicator progress across 17 SDGs."),
            ("TECH_DATAVIZ", 4, 4, "Essential for high-impact analytical visualizations and research papers."),
            ("BEH_COMM", 4, 4, "Necessary for publishing official research monographs and reports.")
        ],
        "Assistant Director": [
            ("STAT_IND", 4, 4, "Required for overseeing Annual Survey of Industries and IIP computation."),
            ("STAT_NAT_ACC", 4, 4, "Key for macroeconomic reconciliation with National Accounts Division."),
            ("BEH_LEAD", 5, 5, "Primary managerial requirement for heading divisional operational wings."),
            ("BEH_COMM", 4, 4, "Essential for inter-ministerial coordination and executive briefings."),
            ("GOV_CYBER", 4, 4, "Required for divisional data governance and information security compliance."),
            ("STAT_QUALITY", 4, 4, "Oversees quality audits and NQAF standard enforcement.")
        ],
        "National Accounts Estimator": [
            ("STAT_NAT_ACC", 5, 5, "Core mastery of SNA 2008 framework, GDP, and input-output tables."),
            ("TECH_PYTHON", 3, 3, "Used for macro aggregation scripts and time-series reconciliation."),
            ("TECH_SQL", 4, 4, "Vital for querying company finances (MCA21) and ASI databases."),
            ("STAT_IND", 4, 4, "Required for industrial output and GVA estimation."),
            ("STAT_PRICE", 4, 4, "Essential for constant price deflators and price index adjustments.")
        ],
        "SDG Monitoring Officer": [
            ("STAT_SDG", 5, 5, "Direct oversight of 300+ national indicators and UN reporting."),
            ("TECH_DATAVIZ", 4, 4, "Needed for SDG progress dashboards and state rankings."),
            ("STAT_QUALITY", 4, 4, "Ensures harmonized data feeds from line ministries."),
            ("BEH_COMM", 4, 4, "Prepares high-level National SDG Progress Reports."),
            ("TECH_OPENDATA", 4, 4, "Publishes SDG datasets on open portals.")
        ],
        "Econometric Modeler": [
            ("TECH_R", 5, 5, "Advanced econometric modeling, ARIMA, and structural equation models."),
            ("TECH_STATA", 4, 4, "Panel data regressions and survey econometric estimations."),
            ("TECH_PYTHON", 4, 4, "Machine learning models and big data processing."),
            ("STAT_NAT_ACC", 4, 4, "Macroeconomic modeling and growth forecasting.")
        ]
    }

    for role_name, reqs in role_requirements_data.items():
        for comp_code, req_lvl, p_weight, rationale in reqs:
            if comp_code in comp_map:
                req_obj = CompetencyRequirement(
                    job_role=role_name,
                    competency_id=comp_map[comp_code],
                    required_level=req_lvl,
                    priority_weight=p_weight,
                    rationale=rationale
                )
                db.add(req_obj)
    db.commit()
    print("[OK] Seeded role-based competency requirements.")

    # -------------------------------------------------------------
    # 4. 100+ SYNTHETIC EMPLOYEES (with 5 Showcase Personas + 1 Admin)
    # -------------------------------------------------------------
    first_names = [
        "Ravi", "Priya", "Amit", "Neha", "Arjun", "Sunita", "Rajesh", "Ananya", "Vikram", "Meera",
        "Deepak", "Kavita", "Suresh", "Pooja", "Manoj", "Shilpa", "Gaurav", "Divya", "Alok", "Nandini",
        "Rohan", "Sneha", "Kunal", "Swati", "Naveen", "Archana", "Sanjay", "Tanvi", "Pradeep", "Rashmi",
        "Abhishek", "Geeta", "Harish", "Aparna", "Varun", "Bhavna", "Kishore", "Pallavi", "Satish", "Chitra",
        "Girish", "Madhavi", "Hemant", "Renu", "Tarun", "Vandana", "Mahesh", "Jyoti", "Nilesh", "Uma"
    ]
    last_names = [
        "Kumar", "Sharma", "Verma", "Singh", "Rao", "Patel", "Gupta", "Mukherjee", "Iyer", "Nair",
        "Joshi", "Reddy", "Menon", "Agarwal", "Deshmukh", "Hegde", "Bose", "Choudhury", "Bhat", "Pillai",
        "Mishra", "Pandey", "Saxena", "Shukla", "Tripathi", "Banerjee", "Dutta", "Ghosh", "Sengupta", "Chatterjee"
    ]

    # Pre-defined showcase personas
    showcase_employees = [
        {
            "employee_id": "OSS1001",
            "name": "Ravi Kumar",
            "email": "ravi.kumar@mospi.gov.in",
            "department": "National Accounts Division",
            "department_code": "NAD",
            "designation": "Statistical Officer",
            "job_role": "Statistical Data Analyst",
            "current_assignment": "National Accounts Analysis",
            "education": "M.Sc. Statistics",
            "years_of_experience": 5.0,
            "joining_date": date(2021, 4, 15),
            "previous_trainings": "R Programming, Survey Methodology",
            "competency_domain": "Statistical + Technical",
            "role": "LEARNER",
            # Starting levels: Has gaps in Python (2/4), SQL (3/4), Sampling (3/3), DataViz (2/4), NatAcc (3/4)
            "competency_levels": {
                "TECH_PYTHON": 2,
                "TECH_SQL": 3,
                "STAT_NAT_ACC": 3,
                "TECH_DATAVIZ": 2,
                "STAT_SAMPLING": 3,
                "STAT_QUALITY": 2,
                "GOV_CYBER": 2
            }
        },
        {
            "employee_id": "OSS1002",
            "name": "Priya Sharma",
            "email": "priya.sharma@mospi.gov.in",
            "department": "Price Statistics Division",
            "department_code": "PSD",
            "designation": "Junior Statistical Officer",
            "job_role": "Price Index Statistician",
            "current_assignment": "CPI Rural/Urban Basket Revision",
            "education": "M.Sc. Applied Statistics",
            "years_of_experience": 3.0,
            "joining_date": date(2023, 6, 1),
            "previous_trainings": "Basic Statistical Methods, MS Excel Advanced",
            "competency_domain": "Statistical",
            "role": "LEARNER",
            "competency_levels": {
                "STAT_PRICE": 3,
                "TECH_SQL": 2,
                "TECH_PYTHON": 1,
                "STAT_QUALITY": 3,
                "TECH_DATAVIZ": 2,
                "BEH_COMM": 2
            }
        },
        {
            "employee_id": "OSS1003",
            "name": "Amit Verma",
            "email": "amit.verma@mospi.gov.in",
            "department": "Field Operations Division",
            "department_code": "FOD",
            "designation": "Statistical Officer",
            "job_role": "Survey Operations Specialist",
            "current_assignment": "PLFS Field Monitoring & Allocation",
            "education": "M.Stat (ISI)",
            "years_of_experience": 6.0,
            "joining_date": date(2020, 2, 10),
            "previous_trainings": "Field Survey Protocols, Stratified Sampling",
            "competency_domain": "Statistical + Managerial",
            "role": "LEARNER",
            "competency_levels": {
                "STAT_SURVEY": 4,
                "STAT_SAMPLING": 3,
                "STAT_LABOUR": 3,
                "BEH_LEAD": 3,
                "TECH_GIS": 2,
                "GOV_PRIVACY": 3
            }
        },
        {
            "employee_id": "OSS1004",
            "name": "Neha Singh",
            "email": "neha.singh@mospi.gov.in",
            "department": "Data Informatics & Innovation Division",
            "department_code": "DIID",
            "designation": "Research Officer",
            "job_role": "Research Officer",
            "current_assignment": "DIID Big Data Informatics",
            "education": "M.Sc. Data Science",
            "years_of_experience": 4.0,
            "joining_date": date(2022, 9, 1),
            "previous_trainings": "Python for Data Analysis, Machine Learning Fundamentals",
            "competency_domain": "Technical + Statistical",
            "role": "LEARNER",
            "competency_levels": {
                "TECH_PYTHON": 3,
                "TECH_R": 2,
                "TECH_AIML": 2,
                "STAT_SDG": 3,
                "TECH_DATAVIZ": 3,
                "BEH_COMM": 3
            }
        },
        {
            "employee_id": "OSS1005",
            "name": "Arjun Rao",
            "email": "arjun.rao@mospi.gov.in",
            "department": "Economic Statistics Division",
            "department_code": "ESD",
            "designation": "Assistant Director",
            "job_role": "Assistant Director",
            "current_assignment": "ASI & Industrial Production Review",
            "education": "M.A. Economics",
            "years_of_experience": 9.0,
            "joining_date": date(2017, 11, 15),
            "previous_trainings": "Executive Leadership in MoSPI, Macroeconomic Policy",
            "competency_domain": "Managerial + Statistical",
            "role": "LEARNER",
            "competency_levels": {
                "STAT_IND": 3,
                "STAT_NAT_ACC": 3,
                "BEH_LEAD": 4,
                "BEH_COMM": 3,
                "GOV_CYBER": 3,
                "STAT_QUALITY": 3
            }
        }
    ]

    all_employees_to_insert = []
    
    # Add showcase employees
    for emp_data in showcase_employees:
        all_employees_to_insert.append(emp_data)

    # Add Admin user
    admin_user = User(
        employee_id="ADMIN001",
        password_hash=admin_pass_hash,
        role="ADMIN",
        is_active=True
    )
    db.add(admin_user)

    admin_emp = Employee(
        employee_id="ADMIN001",
        name="Admin Official",
        email="admin.diid@mospi.gov.in",
        department="Data Informatics & Innovation Division",
        department_code="DIID",
        designation="Joint Director (IT & Capacity)",
        job_role="Administrative & IT Statistician",
        current_assignment="National Statistical Capacity Building Portal",
        education="M.Tech / M.Stat",
        years_of_experience=15.0,
        joining_date=date(2011, 1, 10),
        previous_trainings="Enterprise IT Governance, e-Office, Security Protocols",
        competency_domain="Digital Governance + Management",
        role="ADMIN"
    )
    db.add(admin_emp)

    # Generate additional 105 synthetic employees to reach 110 total
    roles_pool = list(role_requirements_data.keys())
    depts_pool = departments_data
    educations_pool = ["M.Sc. Statistics", "M.Sc. Applied Statistics", "M.Stat (ISI)", "M.A. Economics", "M.Sc. Data Science", "MCA", "B.Stat (ISI)"]
    trainings_pool = [
        "Survey Sampling & NSS Schedules",
        "R for Official Statistics",
        "Python Data Science Essentials",
        "National Accounts and GVA Compilation",
        "Consumer Price Index Methodology",
        "QGIS for Spatial Sampling",
        "Cybersecurity Awareness & DPDP",
        "Data Visualization & Power BI",
        "PLFS Field Operations & Monitoring",
        "Time-Series Econometrics with Stata"
    ]
    assignments_pool = {
        "NAD": ["Quarterly GDP Estimates", "State GSDP Harmonization", "Informal Sector GVA Compilation", "Capital Stock Estimation"],
        "PSD": ["Monthly CPI Rural Index", "CPI Urban Price Verification", "Wholesale & Producer Price Indicators", "Base Year Revision"],
        "FOD": ["PLFS Field Supervision Phase II", "Annual Survey of Unincorporated Enterprises", "Regional Office Audit", "Enumerator Training"],
        "SDRD": ["Sampling Frame Preparation (UFS)", "Survey Schedule 10.2 Review", "Variance Estimation Algorithms", "Pilot Survey on Services"],
        "SSD": ["SDG National Indicator Monitoring", "Gender Statistics & Time Use Survey", "Social Welfare Indicators", "Disability Statistics"],
        "ESD": ["Annual Survey of Industries (ASI)", "Index of Industrial Production (IIP)", "Energy Statistics Compilation", "Services Trade Survey"],
        "DIID": ["National Data Archive (NADA)", "Microdata Dissemination API", "AI Data Quality Scanner", "Cloud Migration Strategy"],
        "CPD": ["Statistical Year Book Publication", "SAARC & UN Statistical Coordination", "Official Statistics Dissemination", "MoSPI Newsletter"]
    }

    start_num = 1006
    for i in range(105):
        emp_id = f"OSS{start_num + i}"
        fn = first_names[i % len(first_names)]
        ln = last_names[(i * 3) % len(last_names)]
        full_name = f"{fn} {ln}"
        dept_obj = depts_pool[i % len(depts_pool)]
        dept_name = dept_obj["name"]
        dept_code = dept_obj["code"]

        role_name = roles_pool[i % len(roles_pool)]
        
        # Designations based on experience
        exp = round(random.uniform(1.5, 18.0), 1)
        if exp < 3.0:
            desig = "Junior Statistical Officer"
        elif exp < 7.0:
            desig = "Statistical Officer"
        elif exp < 12.0:
            desig = "Senior Statistical Officer"
        else:
            desig = "Assistant Director"

        assign_list = assignments_pool.get(dept_code, ["Statistical Analysis & Research"])
        assignment = assign_list[i % len(assign_list)]
        edu = educations_pool[i % len(educations_pool)]
        tr = trainings_pool[i % len(trainings_pool)]
        join_year = 2026 - int(exp)
        join_date = date(join_year, random.randint(1, 12), random.randint(1, 28))

        all_employees_to_insert.append({
            "employee_id": emp_id,
            "name": full_name,
            "email": f"{fn.lower()}.{ln.lower()}{i+1}@mospi.gov.in",
            "department": dept_name,
            "department_code": dept_code,
            "designation": desig,
            "job_role": role_name,
            "current_assignment": assignment,
            "education": edu,
            "years_of_experience": exp,
            "joining_date": join_date,
            "previous_trainings": tr,
            "competency_domain": "Statistical + Technical",
            "role": "LEARNER",
            "competency_levels": None # Will assign random realistic levels
        })

    # Insert all employees and create User accounts
    for emp_info in all_employees_to_insert:
        user = User(
            employee_id=emp_info["employee_id"],
            password_hash=demo_pass_hash,
            role=emp_info.get("role", "LEARNER"),
            is_active=True
        )
        db.add(user)

        emp = Employee(
            employee_id=emp_info["employee_id"],
            name=emp_info["name"],
            email=emp_info["email"],
            department=emp_info["department"],
            department_code=emp_info["department_code"],
            designation=emp_info["designation"],
            job_role=emp_info["job_role"],
            current_assignment=emp_info["current_assignment"],
            education=emp_info["education"],
            years_of_experience=emp_info["years_of_experience"],
            joining_date=emp_info["joining_date"],
            previous_trainings=emp_info["previous_trainings"],
            competency_domain=emp_info["competency_domain"],
            role=emp_info.get("role", "LEARNER")
        )
        db.add(emp)
        db.flush()

        # Seed employee competencies
        specified_levels = emp_info.get("competency_levels")
        if specified_levels:
            for c_code, lvl in specified_levels.items():
                if c_code in comp_map:
                    ec = EmployeeCompetency(
                        employee_id=emp.employee_id,
                        competency_id=comp_map[c_code],
                        current_level=lvl,
                        assessed_level=lvl,
                        verified_by_assessment=(lvl >= 3),
                        source="Initial Profile"
                    )
                    db.add(ec)
        else:
            # Assign realistic levels based on job role requirements with variation
            role_reqs = role_requirements_data.get(emp.job_role, [])
            for c_code, req_lvl, _, _ in role_reqs:
                if c_code in comp_map:
                    # Give current level around req_lvl - 1 or req_lvl - 2 (realistic gap)
                    cur_lvl = max(1, min(5, req_lvl - random.choice([0, 1, 1, 2, 2, 3])))
                    ec = EmployeeCompetency(
                        employee_id=emp.employee_id,
                        competency_id=comp_map[c_code],
                        current_level=cur_lvl,
                        assessed_level=cur_lvl,
                        verified_by_assessment=(cur_lvl >= 3),
                        source="Initial Profile"
                    )
                    db.add(ec)

    db.commit()
    print(f"[OK] Seeded {len(all_employees_to_insert) + 1} employees and user accounts.")

    # -------------------------------------------------------------
    # 5. 50+ iGOT KARMAYOGI COURSES (Verified Prototype Catalogue)
    # -------------------------------------------------------------
    igot_courses_data = [
        ("IGOT_PY_101", "Python for Data Analysis in Public Administration", "ISTM / DoPT", "Master NumPy, pandas, data aggregation, and statistical transformations for official survey datasets.", 8.0, "Python for Data Analysis, Data Visualization, Data Quality Frameworks", "Technical", "Intermediate"),
        ("IGOT_SQL_101", "Relational Database Management and SQL for Government", "National Informatics Centre (NIC)", "Writing complex SELECT queries, indexing, joins, and aggregates for administrative databases.", 6.0, "SQL & Database Queries, APIs & Data Integration", "Technical", "Intermediate"),
        ("IGOT_SNA_201", "Fundamentals of System of National Accounts (SNA 2008)", "MoSPI / NSSTA", "Comprehensive introduction to Gross Value Added (GVA), GDP compilation, and institutional sectors.", 10.0, "National Accounts, Price Statistics, Metadata Standards", "Statistical", "Advanced"),
        ("IGOT_SURV_101", "Official Survey Design & Multi-Stage Sampling", "NSSTA Greater Noida", "Principles of sampling frames, probability proportional to size (PPS), and sampling variance.", 12.0, "Survey Design, Sampling Techniques, Labour Statistics", "Statistical", "Advanced"),
        ("IGOT_CPI_101", "Compilation Methodology of Consumer Price Index (CPI)", "Price Statistics Division / MoSPI", "Basket selection, price collection protocols, Laspeyres aggregation, and imputation.", 6.5, "Price Statistics, Data Quality Frameworks, National Accounts", "Statistical", "Intermediate"),
        ("IGOT_R_101", "Statistical Computing and Data Analysis with R", "Indian Statistical Institute / DoPT", "Data frames, survey package, hypothesis testing, and econometric regression in R.", 9.0, "R Programming, Data Visualization & Dashboards, Sampling Techniques", "Technical", "Intermediate"),
        ("IGOT_SDG_101", "Monitoring Sustainable Development Goals (SDG NIF)", "NITI Aayog & MoSPI", "Understanding the National Indicator Framework, data disaggregation, and metadata standards.", 5.0, "SDG Indicators, Metadata Standards, Data Visualization & Dashboards", "Statistical", "Beginner"),
        ("IGOT_CYBER_101", "Cybersecurity and Data Protection for Government Officials", "MeitY / CERT-In", "Information security guidelines, password protocols, phishing defense, and server hygiene.", 4.0, "Cybersecurity & Data Protection, Data Privacy & Anonymization, Digital Governance", "Digital Governance", "Beginner"),
        ("IGOT_DPDP_101", "Digital Personal Data Protection (DPDP) Act Compliance", "DoPT / Ministry of Law", "De-identification techniques, respondent consent, and microdata privacy standards.", 4.5, "Data Privacy & Anonymization, Cybersecurity & Data Protection, Digital Governance", "Digital Governance", "Intermediate"),
        ("IGOT_VIZ_101", "Data Storytelling & Executive Visualizations", "ISTM New Delhi", "Creating charts, dashboard design, visual clarity, and statistical reporting best practices.", 5.5, "Data Visualization & Dashboards, Official Communication & Reporting, Python for Data Analysis", "Technical", "Intermediate"),
        ("IGOT_GIS_101", "Geospatial Analysis and QGIS for Public Systems", "Department of Space / ISRO", "Spatial coordinates, layer overlays, choropleth generation, and block mapping.", 7.5, "GIS & Spatial Statistics, Survey Design, Data Visualization & Dashboards", "Technical", "Intermediate"),
        ("IGOT_ETHICS_101", "Ethics, Objectivity and Integrity in Public Service", "DoPT / Lal Bahadur Shastri National Academy", "Constitutional values, impartiality in official statistics, and public trust.", 3.0, "Public Service Ethics & Integrity, Leadership & Team Management", "Behavioural / Managerial", "Beginner"),
        ("IGOT_LEAD_101", "Leadership in Field Operations and Team Dynamics", "IIPA New Delhi", "Leading diverse survey enumerators, dispute resolution, and field mission success.", 6.0, "Leadership & Team Management, Official Communication & Reporting", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_PLFS_101", "Periodic Labour Force Survey (PLFS) Concepts & Standards", "Social Statistics Division", "Usual Principal Activity Status (UPSS), Current Weekly Status (CWS), and LFPR estimation.", 7.0, "Labour Statistics, Survey Design, Sampling Techniques", "Statistical", "Intermediate"),
        ("IGOT_ASI_101", "Annual Survey of Industries (ASI): Concepts & Data Flow", "Economic Statistics Division", "NIC classification, capital invested, gross output, and factory sector survey rounds.", 8.0, "Industrial Statistics, National Accounts, Data Quality Frameworks", "Statistical", "Advanced"),
        ("IGOT_QUAL_101", "National Quality Assurance Framework (NQAF) for Official Data", "MoSPI Quality Wing", "Data audit protocols, consistency checks, outlier detection, and statistical validation.", 5.0, "Data Quality Frameworks, Metadata Standards, Survey Design", "Statistical", "Intermediate"),
        ("IGOT_API_101", "Open Data Publishing and Web APIs for Statistics", "NIC / Open Data Portal", "REST APIs, JSON formats, automated data exchange pipelines, and data.gov.in standards.", 4.5, "APIs & Data Integration, Open Data Standards, Cloud Computing for Government", "Technical", "Intermediate"),
        ("IGOT_ML_101", "Applied Machine Learning for Survey Data Validation", "Digital India / MoSPI DIID", "Classification models, automated survey outlier detection, and text categorization.", 10.0, "AI & Machine Learning in Statistics, Python for Data Analysis, Data Quality Frameworks", "Technical", "Advanced"),
        ("IGOT_TIME_101", "Time Series Forecasting and Econometric Analysis", "Institute of Economic Growth", "ARIMA models, seasonal adjustment (X-13ARIMA-SEATS), and macroeconomic forecasting.", 8.5, "R Programming, National Accounts, Price Statistics", "Technical", "Advanced"),
        ("IGOT_REPORT_101", "Drafting Statistical Reports and Parliamentary Briefs", "ISTM New Delhi", "Structuring executive summaries, bulleted statistical highlights, and evidence briefs.", 4.0, "Official Communication & Reporting, Leadership & Team Management, Metadata Standards", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_CLOUD_101", "Government Cloud (MeghRaj) Fundamentals", "NIC Cloud Services", "Cloud infrastructure, secure data hosting, containerization, and high availability.", 4.0, "Cloud Computing for Government, Cybersecurity & Data Protection", "Digital Governance", "Beginner"),
        ("IGOT_STATA_101", "Econometric and Survey Analysis with Stata", "NCAER / MoSPI", "Survey weights (svyset), complex survey regression, and microdata panel analysis.", 7.5, "Stata Econometrics, Sampling Techniques, Labour Statistics", "Technical", "Advanced"),
        ("IGOT_SPSS_101", "Applied Social Research and Data Analysis with SPSS", "TISS Mumbai", "Cross-tabulation, Chi-square tests, correlation, and survey table generation.", 6.0, "SPSS Statistics, Survey Design", "Technical", "Intermediate"),
        ("IGOT_META_101", "Statistical Data and Metadata eXchange (SDMX) Basics", "MoSPI DIID", "SDMX architecture, data structure definitions (DSD), and global dissemination formats.", 5.0, "Metadata Standards, APIs & Data Integration, Open Data Standards", "Statistical", "Intermediate"),
        ("IGOT_AGRI_101", "Agricultural Statistics and Land Use Classification", "Directorate of Economics & Statistics", "Crop cutting experiments, area enumeration, and agricultural input cost indices.", 6.0, "Agricultural Statistics, Sampling Techniques, Survey Design", "Statistical", "Intermediate"),
        ("IGOT_DPI_101", "Digital Public Infrastructure in Governance (India Stack)", "National e-Governance Division (NeGD)", "Architecture of Aadhaar authentication, UPI, DigiLocker, and API Setu.", 4.0, "Digital Public Infrastructure, Cloud Computing for Government", "Digital Governance", "Beginner"),
        ("IGOT_SAS_101", "Enterprise SAS Programming for Large Scale Census Data", "National Academy of Statistical Administration", "DATA step programming, PROC SQL, and macro programming in SAS.", 8.0, "SAS Analytics, SQL & Database Queries", "Technical", "Advanced"),
        ("IGOT_DEC_101", "Evidence-Based Decision Making in Public Policy", "NITI Aayog / CBC", "Transforming raw statistical indicators into actionable policy interventions and memos.", 5.0, "Evidence-Based Decision Making, Official Communication & Reporting", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_CHG_101", "Change Management & Modernization in Public Systems", "IIPA New Delhi", "Leading digital transformation, managing resistance, and agile workflows in government.", 4.5, "Change Management in Governance, Leadership & Team Management", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_PY_201", "Advanced Python: Data Pipelines and Automation", "NIC / Digital India", "Building production-grade ETL scripts, cron automations, and data validation suites in Python.", 9.0, "Python for Data Analysis, APIs & Data Integration, Data Quality Frameworks", "Technical", "Advanced"),
        ("IGOT_SQL_201", "Advanced SQL Window Functions and Analytical Aggregations", "NIC Training Wing", "Partitioning, lead/lag functions, recursive queries, and database optimization.", 6.5, "SQL & Database Queries, Python for Data Analysis", "Technical", "Advanced"),
        ("IGOT_SNA_301", "Quarterly GDP and High-Frequency Economic Tracking", "National Accounts Division", "Benchmarking techniques (Denton method), leading indicator models, and seasonal adjustments.", 9.5, "National Accounts, Price Statistics, Industrial Statistics", "Statistical", "Advanced"),
        ("IGOT_SURV_201", "Computer-Assisted Personal Interviewing (CAPI) Deployment", "NSSTA Greater Noida", "Survey solutions, CSPro scripting, real-time validation rules, and GPS tag verification.", 6.0, "Survey Design, Data Quality Frameworks, GIS & Spatial Statistics", "Statistical", "Intermediate"),
        ("IGOT_CPI_201", "Hedonic Pricing and Web Scraping for Inflation Monitoring", "Price Statistics Division", "Modern price collection methods, e-commerce web scraping, and quality adjustment algorithms.", 7.0, "Price Statistics, Python for Data Analysis, AI & Machine Learning in Statistics", "Statistical", "Advanced"),
        ("IGOT_R_201", "Applied Econometrics and Panel Data in R", "ISI Kolkata / DoPT", "Fixed effects, random effects, GMM estimators, and instrumental variable analysis.", 10.0, "R Programming, National Accounts, Labour Statistics", "Technical", "Advanced"),
        ("IGOT_SDG_201", "State & UT SDG Index Construction and Tracking", "NITI Aayog", "Target setting, normalization techniques, composite index scoring, and dashboarding.", 5.5, "SDG Indicators, Data Visualization & Dashboards, Official Communication & Reporting", "Statistical", "Intermediate"),
        ("IGOT_CYBER_201", "Incident Handling and CERT-In Security Protocols", "CERT-In / MeitY", "Log analysis, vulnerability assessment, breach escalation, and encryption standards.", 5.0, "Cybersecurity & Data Protection, Cloud Computing for Government", "Digital Governance", "Intermediate"),
        ("IGOT_DPDP_201", "Statistical Disclosure Control & Microdata Anonymization", "MoSPI Data Innovation Lab", "SDC techniques, perturbation, top-coding, k-anonymity, and l-diversity in public releases.", 6.5, "Data Privacy & Anonymization, Data Quality Frameworks, Metadata Standards", "Digital Governance", "Advanced"),
        ("IGOT_VIZ_201", "Interactive BI Dashboard Engineering for MoSPI Indicators", "NIC Analytics Wing", "Connecting live SQL databases to interactive dashboards with drill-downs and role filters.", 7.0, "Data Visualization & Dashboards, SQL & Database Queries, APIs & Data Integration", "Technical", "Advanced"),
        ("IGOT_GIS_201", "Spatial Statistics and Hotspot Analysis for Socio-Economic Data", "ISRO / NSSTA", "Moran's I, Getis-Ord Gi*, kernel density estimation, and district-level vulnerability maps.", 8.0, "GIS & Spatial Statistics, SDG Indicators, Survey Design", "Technical", "Advanced"),
        ("IGOT_PROJ_101", "Project Management in Large-Scale Statistical Surveys", "ISTM New Delhi", "Gantt charts, milestone tracking, resource allocation, and quality risk registers.", 6.0, "Project Management in Statistical Surveys, Leadership & Team Management", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_LABOUR_201", "Informal Sector & Unorganized Labour Measurement", "V.V. Giri National Labour Institute", "Measuring gig workers, platform economy, social security coverage, and wage differentials.", 6.5, "Labour Statistics, Survey Design, National Accounts", "Statistical", "Intermediate"),
        ("IGOT_IND_201", "Index of Industrial Production (IIP): Base Revision & Compilation", "Economic Statistics Division", "Item basket weighting, non-response estimation, and item substitution rules.", 7.0, "Industrial Statistics, Price Statistics, Data Quality Frameworks", "Statistical", "Intermediate"),
        ("IGOT_QUAL_201", "Automated Validation Rules and Error Auditing in Survey Portals", "DIID MoSPI", "Developing regex checks, boundary constraints, and consistency matrices for web surveys.", 5.5, "Data Quality Frameworks, Python for Data Analysis, Survey Design", "Statistical", "Intermediate"),
        ("IGOT_OPEN_201", "FAIR Data Principles and Open Government Data (OGD)", "NIC / Open Data Unit", "Findable, Accessible, Interoperable, and Reusable data publishing architectures.", 4.5, "Open Data Standards, Metadata Standards, APIs & Data Integration", "Technical", "Beginner"),
        ("IGOT_ML_201", "Natural Language Processing for Statistical Occupation Coding", "MoSPI DIID / IIIT Delhi", "Automating National Classification of Occupations (NCO) and NIC code assignment using NLP.", 9.0, "AI & Machine Learning in Statistics, Python for Data Analysis, Metadata Standards", "Technical", "Advanced"),
        ("IGOT_CLOUD_201", "Containerization and Docker for Statistical Analytics Pipelines", "NIC Cloud Training", "Packaging Python and R statistical codebases into repeatable Docker images for government cloud.", 6.0, "Cloud Computing for Government, Python for Data Analysis, Cybersecurity & Data Protection", "Digital Governance", "Intermediate"),
        ("IGOT_COMM_201", "Parliamentary Q&A Drafting and Statistical Factsheet Preparation", "MoSPI Coordination Wing", "Answering Starred/Unstarred Questions, rapid fact retrieval, and statistical vetting.", 4.0, "Official Communication & Reporting, Public Service Ethics & Integrity", "Behavioural / Managerial", "Intermediate"),
        ("IGOT_AGRI_201", "Remote Sensing & Satellite Imagery for Agricultural Crop Estimation", "Mahalanobis National Crop Forecast Centre", "NDVI indices, crop area yield modeling, and integration with ground survey cutting.", 8.0, "Agricultural Statistics, GIS & Spatial Statistics, AI & Machine Learning in Statistics", "Statistical", "Advanced"),
        ("IGOT_STATA_201", "Multilevel and Hierarchical Modeling with Stata", "ISI Delhi / NCAER", "Nested random effects, district-level clustering, and survey variance estimation.", 8.5, "Stata Econometrics, Sampling Techniques, Survey Design", "Technical", "Advanced"),
        ("IGOT_DATA_GOV_101", "National Data Governance Framework Policy (NDGFP)", "MeitY / Data Governance Unit", "Framework for anonymized non-personal data sharing, India Data Management Office (IDMO).", 5.0, "Data Privacy & Anonymization, Open Data Standards, Digital Governance", "Digital Governance", "Intermediate")
    ]

    for c in igot_courses_data:
        course = IGOTCourse(
            course_id=c[0],
            title=c[1],
            provider=c[2],
            description=c[3],
            duration_hours=c[4],
            competency_tags=c[5],
            category=c[6],
            difficulty=c[7],
            course_url=f"https://igotkarmayogi.gov.in/learn/course/{c[0].lower()}",
            source="iGOT Karmayogi Prototype Catalogue",
            active=True
        )
        db.add(course)
    db.commit()
    print(f"[OK] Seeded {len(igot_courses_data)} iGOT Karmayogi courses.")

    # -------------------------------------------------------------
    # 6. 30+ NSSTA / TPAC PROGRAMMES (Verified Prototype Catalogue)
    # -------------------------------------------------------------
    nssta_programmes_data = [
        ("NSSTA_PROG_01", "Advanced National Accounts: SUT and Capital Accounting", "NSSTA Greater Noida", "Intensive hands-on residential training on Supply-Use Tables (SUT), asset accounts, and FISIM estimation.", 5, 30.0, "National Accounts, Industrial Statistics, Price Statistics", "Statistical", "Advanced", "ISS / SSS Officers in NAD & ESD"),
        ("NSSTA_PROG_02", "Large-Scale Sample Survey Operations & Quality Control", "NSSTA Greater Noida", "Practical workshop on field sample selection, non-response adjustments, and CAPI survey tools.", 5, 30.0, "Survey Design, Sampling Techniques, Data Quality Frameworks", "Statistical", "Advanced", "Field Operations Division Officers"),
        ("NSSTA_PROG_03", "Price Index Numbers: Advanced Formulae and Hedonic Imputation", "NSSTA & ISI Kolkata", "In-depth training on multilateral price indices, scanner data, and quality-adjusted inflation calculation.", 4, 24.0, "Price Statistics, National Accounts, R Programming", "Statistical", "Advanced", "Price Statistics Division Staff"),
        ("NSSTA_PROG_04", "Data Science & Machine Learning Pipeline for Official Microdata", "MoSPI TPAC / ISI Delhi", "Python, big data frameworks, automated survey verification, and classification algorithms.", 10, 60.0, "Python for Data Analysis, AI & Machine Learning in Statistics, SQL & Database Queries", "Technical", "Advanced", "DIID & Research Officers"),
        ("NSSTA_PROG_05", "Periodic Labour Force Survey (PLFS) Data Extraction & Modeling", "NSSTA Greater Noida", "Hands-on data extraction from raw PLFS unit-level microdata, multiplier application, and transition matrices.", 3, 18.0, "Labour Statistics, Sampling Techniques, Stata Econometrics", "Statistical", "Intermediate", "Social Statistics & Analytical Wings"),
        ("NSSTA_PROG_06", "Geospatial Information System (GIS) for Urban Frame Survey", "NSSTA & Regional Remote Sensing Centre", "High-resolution satellite mapping, UFS block boundary delineation, and GIS database construction.", 5, 30.0, "GIS & Spatial Statistics, Survey Design, Data Visualization & Dashboards", "Technical", "Intermediate", "SDRD & FOD Officers"),
        ("NSSTA_PROG_07", "Annual Survey of Industries (ASI) Estimation Methodology", "NSSTA Greater Noida", "Factory sector frame maintenance, pool of samples, multiplier weighting, and GVA reconciliation.", 4, 24.0, "Industrial Statistics, National Accounts, Data Quality Frameworks", "Statistical", "Advanced", "ESD & Regional Officials"),
        ("NSSTA_PROG_08", "SDG Indicator Computation and National Metadata Validation", "MoSPI & UN SIAP", "Aligning national administrative data sources with UN custodian agency SDG calculation methodologies.", 3, 18.0, "SDG Indicators, Metadata Standards, Data Quality Frameworks", "Statistical", "Intermediate", "SSD and Nodal Statistical Cells"),
        ("NSSTA_PROG_09", "Executive Leadership & Change Management in Statistical Governance", "NSSTA Greater Noida", "Strategic decision-making, modernization of statistical offices, and inter-agency coordination.", 3, 18.0, "Leadership & Team Management, Official Communication & Reporting, Public Service Ethics & Integrity", "Behavioural / Managerial", "Advanced", "Directors & Assistant Directors"),
        ("NSSTA_PROG_10", "Statistical Data Quality Auditing and Imputation Algorithms", "NSSTA & ISI Kolkata", "Deterministic and stochastic imputation (Hot-deck, KNN), outlier bounds, and quality audit trails.", 4, 24.0, "Data Quality Frameworks, Python for Data Analysis, Sampling Techniques", "Statistical", "Advanced", "All Statistical System Analysts"),
        ("NSSTA_PROG_11", "Time Series Econometrics & Seasonal Adjustment for Macro Indicators", "NSSTA & Reserve Bank of India Staff College", "Deep dive into X-13ARIMA-SEATS, unit root testing, cointegration, and quarterly GDP reconciliation.", 5, 30.0, "National Accounts, Price Statistics, R Programming", "Statistical", "Advanced", "National Accounts & Macro Analysts"),
        ("NSSTA_PROG_12", "Survey Sampling Frames and Digital Mapping for Field Enumeration", "NSSTA & Survey of India", "Digitizing village cadastre maps, cluster boundary tracking, and mobile GIS verification.", 4, 24.0, "Survey Design, Sampling Techniques, GIS & Spatial Statistics", "Statistical", "Intermediate", "FOD & SDRD Sampling Officers"),
        ("NSSTA_PROG_13", "Advanced R for Official Statistics: Survey Weighting & Demography", "MoSPI TPAC / ISI Kolkata", "Complex survey designs with the 'survey' and 'srvyr' packages, life tables, and fertility indices.", 6, 36.0, "R Programming, Sampling Techniques, Labour Statistics", "Technical", "Advanced", "Research Officers & Statistical Analysts"),
        ("NSSTA_PROG_14", "Python Big Data Processing for National Metadata Repositories", "MoSPI TPAC / IIIT Delhi", "PySpark, Dask, automated parsing of millions of census and survey microdata records.", 8, 48.0, "Python for Data Analysis, APIs & Data Integration, Metadata Standards", "Technical", "Advanced", "DIID Software & Database Engineers"),
        ("NSSTA_PROG_15", "Cybersecurity Incident Response & Cloud Security for MoSPI Systems", "MeitY / CERT-In & NSSTA", "Hardening Linux servers, database encryption at rest, secure API gateways, and penetration audit drills.", 3, 18.0, "Cybersecurity & Data Protection, Cloud Computing for Government, Data Privacy & Anonymization", "Digital Governance", "Intermediate", "IT Officers & Systems Administrators"),
        ("NSSTA_PROG_16", "Statistical Disclosure Control Workshop: Anonymizing Microdata Releases", "NSSTA Greater Noida & Statistics Netherlands", "Practical exercises with argus and sdcMicro packages, frequency tables, and microdata release risk.", 3, 18.0, "Data Privacy & Anonymization, Data Quality Frameworks, Metadata Standards", "Digital Governance", "Advanced", "Data Dissemination & Publication Officers"),
        ("NSSTA_PROG_17", "Agricultural Crop Estimation and Area Enumeration Protocols", "NSSTA & ICAR-IASRI", "Design of General Crop Estimation Surveys (GCES), remote sensing ground truthing, and yield estimation.", 5, 30.0, "Agricultural Statistics, Sampling Techniques, Survey Design", "Statistical", "Intermediate", "State Statistical Bureaus & DES Officers"),
        ("NSSTA_PROG_18", "Index of Industrial Production: Practical Compilation & Diagnostics", "ESD MoSPI & NSSTA", "Source agency data collection, non-response imputation, and sub-index volatility troubleshooting.", 3, 18.0, "Industrial Statistics, Price Statistics, Data Quality Frameworks", "Statistical", "Intermediate", "ESD Industrial Statistics Cell"),
        ("NSSTA_PROG_19", "Effective Parliamentary Reporting & Statistical Data Communication", "NSSTA & ISTM", "Crafting evidence-based replies, executive dashboard narratives, and media engagement guidelines.", 3, 18.0, "Official Communication & Reporting, Evidence-Based Decision Making", "Behavioural / Managerial", "Intermediate", "Section Officers & Joint Directors"),
        ("NSSTA_PROG_20", "Applied Stata for Complex Socio-Economic Survey Analysis", "NSSTA & NCAER", "svy prefix commands, multinomial logit on PLFS, and poverty & inequality index estimations.", 5, 30.0, "Stata Econometrics, Labour Statistics, Sampling Techniques", "Technical", "Advanced", "Social Statistics & Analytical Division"),
        ("NSSTA_PROG_21", "Machine Learning for Automated Document Extraction & Classification", "MoSPI TPAC / IIT Delhi", "Transformer models, OCR pipelines for historical survey gazettes, and tabular text extraction.", 8, 48.0, "AI & Machine Learning in Statistics, Python for Data Analysis, APIs & Data Integration", "Technical", "Advanced", "Data Innovation & AI Officers"),
        ("NSSTA_PROG_22", "National Quality Assurance Framework (NQAF) Assessor Certification", "NSSTA & MoSPI Quality Directorate", "Training to become certified internal quality auditors for official surveys and administrative registries.", 4, 24.0, "Data Quality Frameworks, Metadata Standards, Survey Design", "Statistical", "Advanced", "Supervisory & Audit Officers"),
        ("NSSTA_PROG_23", "Energy Balance & Environmental-Economic Accounting (SEEA)", "NSSTA Greater Noida & UN SIAP", "System of Environmental-Economic Accounting, asset accounts for minerals, water, and forests.", 5, 30.0, "National Accounts, SDG Indicators, Metadata Standards", "Statistical", "Advanced", "Social & Economic Statistics Officers"),
        ("NSSTA_PROG_24", "Spatial Autocorrelation and Point Pattern Analysis in Public Health Data", "NSSTA & Regional Remote Sensing Centre", "K-function, Voronoi tessellation, disease mapping, and accessibility analysis using QGIS and R.", 4, 24.0, "GIS & Spatial Statistics, R Programming, SDG Indicators", "Technical", "Intermediate", "Social Statistics & Health Survey Units"),
        ("NSSTA_PROG_25", "Public Procurement & Project Governance for Statistical Operations", "NSSTA & Department of Expenditure", "GeM portal, QCBS procurement for field survey agencies, and contract administration.", 3, 18.0, "Project Management in Statistical Surveys, Public Service Ethics & Integrity", "Behavioural / Managerial", "Intermediate", "Administrative & Operational Heads"),
        ("NSSTA_PROG_26", "SDMX Architecture and Automated Data Dissemination Systems", "NSSTA & Eurostat Experts", "Configuring SDMX registries, data structure definitions, and REST web services for national data.", 4, 24.0, "Metadata Standards, APIs & Data Integration, Open Data Standards", "Statistical", "Advanced", "DIID Portal Administrators"),
        ("NSSTA_PROG_27", "Consumer Expenditure Survey (CES) Methodology & Consumption Baskets", "NSSTA & Survey Division", "Recall periods (URP, MRP, MMRP), food/non-food classification, and poverty line consumption deflators.", 4, 24.0, "Survey Design, Price Statistics, Sampling Techniques", "Statistical", "Advanced", "Survey Design & Research Division"),
        ("NSSTA_PROG_28", "Automated Web Scraping and Big Data Ingestion for Official Statistics", "MoSPI TPAC / ISI Bangalore", "BeautifulSoup, Scrapy, Selenium for high-frequency commodity prices and labor market job postings.", 5, 30.0, "Python for Data Analysis, Price Statistics, Labour Statistics", "Technical", "Advanced", "Price Statistics & Research Officers"),
        ("NSSTA_PROG_29", "Digital Signatures, e-Office Governance & Cyber Ethics", "NSSTA & NIC", "e-Office workflows, DSC management, secure file archiving, and RTI compliance in statistical departments.", 2, 12.0, "Digital Public Infrastructure, Cybersecurity & Data Protection, Public Service Ethics & Integrity", "Digital Governance", "Beginner", "All Statistical Staff"),
        ("NSSTA_PROG_30", "Statistical Leadership, Crisis Management & Team Resilience", "NSSTA & IIM Lucknow", "Leading through high-stakes survey deadlines, media scrutiny, and cross-functional team motivation.", 3, 18.0, "Leadership & Team Management, Change Management in Governance, Official Communication & Reporting", "Behavioural / Managerial", "Advanced", "Joint Directors & Deputy Directors"),
        ("NSSTA_PROG_31", "International Classification Systems: NIC, NAPCS, and NCO Harmonization", "NSSTA & CPD MoSPI", "Harmonizing national classification standards with UN ISIC Rev.4, CPC, and ISCO-08.", 3, 18.0, "Metadata Standards, Industrial Statistics, Labour Statistics", "Statistical", "Intermediate", "All Classification & Survey Officers")
    ]

    for p in nssta_programmes_data:
        prog = NSSTAProgramme(
            training_id=p[0],
            title=p[1],
            provider=p[2],
            description=p[3],
            duration_days=p[4],
            duration_hours=p[5],
            competency_tags=p[6],
            category=p[7],
            level=p[8],
            target_audience=p[9],
            programme_url=f"https://nssta.gov.in/trainings/view/{p[0].lower()}",
            source="NSSTA / TPAC Prototype Catalogue",
            active=True
        )
        db.add(prog)
    db.commit()
    print(f"[OK] Seeded {len(nssta_programmes_data)} NSSTA / TPAC training programmes.")

    # -------------------------------------------------------------
    # 7. PROFESSIONAL ROLE COMPETENCY ASSESSMENTS & QUESTIONS
    # -------------------------------------------------------------
    assessments_data = [
        {
            "code": "ASSESS_PY_01",
            "title": "Python for Statistical Operations Assessment",
            "category": "Technical",
            "competency_code": "TECH_PYTHON",
            "description": "Evaluates proficiency in pandas DataFrame manipulations, grouping, microdata filtering, and vectorization.",
            "passing_score": 60.0,
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which pandas method is most computationally efficient for merging large survey microdata tables on household IDs?",
                    "a": "pd.concat(axis=1)",
                    "b": "df.merge(on='household_id', how='inner')",
                    "c": "Iterating over DataFrame rows with iterrows()",
                    "d": "df.append() inside a for-loop",
                    "correct": "B",
                    "explanation": "df.merge utilizes optimized C-level hash joins on indexed keys, outperforming iteration."
                },
                {
                    "text": "In official survey analysis with Python, how should multiplier weights be applied to calculate weighted mean expenditure?",
                    "a": "(df['expenditure'] * df['multiplier']).sum() / df['multiplier'].sum()",
                    "b": "df['expenditure'].mean() * df['multiplier'].mean()",
                    "c": "df['expenditure'].sum() / len(df)",
                    "d": "np.mean(df['expenditure'] + df['multiplier'])",
                    "correct": "A",
                    "explanation": "Weighted mean requires summing the products of value and multiplier, divided by the total sum of multipliers."
                },
                {
                    "text": "Which library in Python is standard for computing descriptive summary statistics and robust linear regressions?",
                    "a": "statsmodels / scipy.stats",
                    "b": "tkinter",
                    "c": "requests",
                    "d": "cryptography",
                    "correct": "A",
                    "explanation": "statsmodels and scipy.stats are the primary scientific packages for statistical testing and regression."
                },
                {
                    "text": "When handling missing survey codes like 999 or -1 in a pandas column, what is the best practice before computing aggregates?",
                    "a": "Leave them as numeric 999 values",
                    "b": "Replace them with np.nan using df.replace()",
                    "c": "Delete the entire DataFrame",
                    "d": "Convert the column to string type",
                    "correct": "B",
                    "explanation": "Replacing sentinel values with np.nan prevents skewing statistical means and variance calculations."
                },
                {
                    "text": "What is the purpose of using vectorization in NumPy instead of Python native for-loops for survey aggregations?",
                    "a": "Vectorization executes operations in optimized C arrays with SIMD instructions, boosting execution speed.",
                    "b": "Vectorization encrypts survey responses automatically.",
                    "c": "Vectorization reduces the need for sampling frames.",
                    "d": "It converts tabular data into PDF format.",
                    "correct": "A",
                    "explanation": "Vectorized operations run in compiled low-level routines without Python bytecode overhead."
                }
            ]
        },
        {
            "code": "ASSESS_NAT_ACC_01",
            "title": "National Accounts & GVA Framework Assessment",
            "category": "Statistical",
            "competency_code": "STAT_NAT_ACC",
            "description": "Evaluates knowledge of SNA 2008 standards, Gross Value Added, GDP identity, and deflators.",
            "passing_score": 60.0,
            "difficulty": "Advanced",
            "questions": [
                {
                    "text": "Under the SNA 2008 methodology adopted by MoSPI, Gross Value Added (GVA) at basic prices is defined as:",
                    "a": "Gross Output at basic prices - Intermediate Consumption at purchasers' prices",
                    "b": "GDP + Product Taxes - Product Subsidies",
                    "c": "Net National Product + Depreciation",
                    "d": "Total Household Final Consumption Expenditure",
                    "correct": "A",
                    "explanation": "GVA at basic prices measures production output minus intermediate consumption used in the production process."
                },
                {
                    "text": "How is GDP at market prices derived from GVA at basic prices?",
                    "a": "GDP = GVA at basic prices + Product Taxes - Product Subsidies",
                    "b": "GDP = GVA at basic prices - Product Taxes + Product Subsidies",
                    "c": "GDP = GVA at basic prices + Import Duties only",
                    "d": "GDP = GVA at basic prices - Operating Surplus",
                    "correct": "A",
                    "explanation": "The standard identity is GDP at market prices = GVA at basic prices + Net Product Taxes (Taxes on Products - Subsidies on Products)."
                },
                {
                    "text": "Which institutional sector is treated as a separate economic entity in India's National Accounts?",
                    "a": "General Government, Financial Corporations, Non-Financial Corporations, Households, and NPISH",
                    "b": "State Governments only",
                    "c": "Foreign tourists exclusively",
                    "d": "Non-tax paying citizens only",
                    "correct": "A",
                    "explanation": "SNA recognizes 5 resident institutional sectors: Non-financial corp, Financial corp, General Government, Households, and NPISH."
                },
                {
                    "text": "What price index is predominantly used as the deflator for converting nominal agricultural output to constant prices in NAD?",
                    "a": "Wholesale Price Index (WPI) / Consumer Price Index for Agricultural Labourers (CPI-AL)",
                    "b": "NASDAQ Index",
                    "c": "Gold spot prices",
                    "d": "Foreign Exchange Forward Rate",
                    "correct": "A",
                    "explanation": "Agricultural output deflation uses relevant WPI component indices and farm harvest prices."
                },
                {
                    "text": "Financial Intermediation Services Indirectly Measured (FISIM) represents:",
                    "a": "The indirect value of financial services provided by banks through interest rate margins rather than explicit fees.",
                    "b": "ATM withdrawal penalties",
                    "c": "Direct income tax on bank branches",
                    "d": "Foreign currency printing charges",
                    "correct": "A",
                    "explanation": "FISIM captures the output of financial intermediaries arising from the spread between deposit and loan interest rates."
                }
            ]
        },
        {
            "code": "ASSESS_SAMPLING_01",
            "title": "Sampling Techniques & Multi-Stage Design Assessment",
            "category": "Statistical",
            "competency_code": "STAT_SAMPLING",
            "description": "Tests concepts of Stratified Multi-Stage Sampling, FSUs, USUs, and design weights.",
            "passing_score": 60.0,
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "In the National Sample Survey (NSS) design for rural sectors, what generally serves as the First Stage Unit (FSU)?",
                    "a": "Census Villages (as per the latest available Population Census)",
                    "b": "Individual households",
                    "c": "District Collectorates",
                    "d": "Gram Panchayats as a single unit",
                    "correct": "A",
                    "explanation": "Census villages serve as the rural sampling frame FSUs, while Urban Frame Survey (UFS) blocks serve urban sectors."
                },
                {
                    "text": "Why is Probability Proportional to Size (PPS) sampling commonly utilized for selecting First Stage Units in surveys?",
                    "a": "To ensure larger villages/blocks have a higher selection probability proportional to their population size.",
                    "b": "To eliminate the need for listing households inside the selected village.",
                    "c": "To ensure every household in the country has an identical non-zero weight without multipliers.",
                    "d": "To reduce the number of survey questionnaires to zero.",
                    "correct": "A",
                    "explanation": "PPS gives larger sampling units a selection probability commensurate with size, improving estimation efficiency."
                },
                {
                    "text": "What is the inverse of the inclusion probability of a sample unit termed in survey estimation?",
                    "a": "Design Weight / Multiplier",
                    "b": "Variance inflation factor",
                    "c": "Standard error limit",
                    "d": "Kurtosis coefficient",
                    "correct": "A",
                    "explanation": "The sampling multiplier is the reciprocal of the joint inclusion probability of the unit."
                },
                {
                    "text": "In two-stage stratified sampling, if stratification reduces within-stratum variance, what is the impact on overall standard error?",
                    "a": "Standard error of the population estimate is reduced.",
                    "b": "Standard error increases infinitely.",
                    "c": "Standard error remains completely unaffected.",
                    "d": "The sample size must be doubled.",
                    "correct": "A",
                    "explanation": "Effective stratification groups homogeneous units, reducing variance and lowering standard error."
                },
                {
                    "text": "What is the purpose of creating sub-samples (e.g. Sub-sample 1 and Sub-sample 2) in NSS survey rounds?",
                    "a": "To enable valid variance estimation and measure inter-penetrating sub-sample differences.",
                    "b": "To allow enumerators to take extra holidays.",
                    "c": "To discard half the collected survey questionnaires.",
                    "d": "To separate male and female respondents into distinct surveys.",
                    "correct": "A",
                    "explanation": "Inter-penetrating sub-samples enable empirical estimation of survey variance and enumerator effects."
                }
            ]
        }
    ]

    for a_data in assessments_data:
        comp_id = comp_map.get(a_data.get("competency_code"))
        assessment = Assessment(
            code=a_data["code"],
            title=a_data["title"],
            category=a_data["category"],
            competency_id=comp_id,
            description=a_data["description"],
            total_questions=len(a_data["questions"]),
            passing_score=a_data["passing_score"],
            time_limit_minutes=15,
            difficulty=a_data["difficulty"],
            is_active=True
        )
        db.add(assessment)
        db.flush()

        for q in a_data["questions"]:
            question = AssessmentQuestion(
                assessment_id=assessment.id,
                competency_id=comp_id,
                question_text=q["text"],
                option_a=q["a"],
                option_b=q["b"],
                option_c=q["c"],
                option_d=q["d"],
                correct_option=q["correct"],
                explanation=q["explanation"],
                difficulty=a_data["difficulty"]
            )
            db.add(question)

    db.commit()
    print(f"[OK] Seeded {len(assessments_data)} role assessments and questions.")

    # -------------------------------------------------------------
    # 8. SEED INITIAL PROGRESS & RECOMMENDATIONS FOR SHOWCASE USERS
    # -------------------------------------------------------------
    # Seed baseline progress for Ravi Kumar (OSS1001)
    db.add(LearningProgress(
        employee_id="OSS1001",
        course_type="iGOT",
        course_id="IGOT_SQL_101",
        title="Relational Database Management and SQL for Government",
        provider="National Informatics Centre (NIC)",
        status="In Progress",
        progress_percentage=65.0,
        hours_spent=4.0,
        competency_name="SQL & Database Queries",
        competency_gain_applied=False,
        enrolled_date=datetime.now(timezone.utc) - timedelta(days=12)
    ))
    db.add(LearningProgress(
        employee_id="OSS1001",
        course_type="NSSTA",
        course_id="NSSTA_PROG_01",
        title="Advanced National Accounts: SUT and Capital Accounting",
        provider="NSSTA Greater Noida",
        status="Completed",
        progress_percentage=100.0,
        hours_spent=30.0,
        competency_name="National Accounts",
        competency_gain_applied=True,
        enrolled_date=datetime.now(timezone.utc) - timedelta(days=60),
        completed_date=datetime.now(timezone.utc) - timedelta(days=55)
    ))
    db.commit()

    # Generate initial personalized recommendations for showcase users
    rec_service = RecommendationService(db)
    for emp_id in ["OSS1001", "OSS1002", "OSS1003", "OSS1004", "OSS1005"]:
        rec_service.generate_recommendations(emp_id, force_refresh=True)

    print("[OK] Generated personalized recommendations and baseline learning progress.")
    db.close()
    print("============================================================")
    print("STATSAKSHAM Database Seeding Completed Successfully!")
    print("============================================================")

if __name__ == "__main__":
    seed_database()
