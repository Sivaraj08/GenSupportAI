import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(output_path):
    # Ensure directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Page setup - 0.75 in margins
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor("#1A365D")   # Deep navy blue
    secondary_color = colors.HexColor("#2B6CB0") # Medium blue
    text_color = colors.HexColor("#2D3748")      # Dark charcoal gray
    accent_color = colors.HexColor("#319795")    # Teal accent
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=15,
        alignment=1 # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=25,
        alignment=1 # Centered
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=5
    )

    story = []
    
    # Header block
    story.append(Paragraph("GenSupport Institute of Technology (GSIT)", title_style))
    story.append(Paragraph("Official Admissions & Support Resource Manual (Academic Year 2026-27)", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 1. Eligibility Criteria
    story.append(Paragraph("1. ELIGIBILITY CRITERIA FOR ADMISSION", h1_style))
    story.append(Paragraph(
        "To secure admission to GenSupport Institute of Technology (GSIT), applicants must meet the following department-wise requirements:",
        body_style
    ))
    
    story.append(Paragraph("<b>Undergraduate Courses (B.E. / B.Tech):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Academic Pathway:</b> Candidates must have completed their 10+2 Higher Secondary Certificate (HSC) or equivalent examination from a recognized central or state board (CBSE, ICSE, State Board, etc.).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Core Subjects:</b> Mandatory passing marks in Physics, Chemistry, and Mathematics (PCM).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Minimum Marks:</b> A minimum aggregate of 50% marks in PCM is required for the General Category (OC). A relaxed minimum of 45% aggregate in PCM is applicable for candidates from reserved categories (OBC, SC, ST).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Computer Science Domain:</b> For B.E. Computer Science and Engineering (CSE) and B.Tech Information Technology (IT), applicants must score a minimum of 60% specifically in Mathematics.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Postgraduate Courses (M.E. / M.Tech):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Degree Requirement:</b> Candidates must possess a B.E. / B.Tech degree in the corresponding engineering discipline with a minimum score of 55% aggregate marks (50% for reserved category candidates).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Entrance Scores:</b> Admissions are based on merit rankings in the national level Graduate Aptitude Test in Engineering (GATE) or state-conducted entrance examinations. GATE qualified candidates are prioritized for allocations.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Management Programs (MBA / MCA):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Undergraduate Degree:</b> Minimum 3-year Bachelor's degree in any discipline with at least 50% aggregate marks.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Specific MCA Prerequisites:</b> Must have studied Mathematics either at the 10+2 level or during their Bachelor's degree.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Testing Scores:</b> A valid score in TANCET, MAT, or CAT is mandatory for MBA enrollment.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 2. Fee Structure
    story.append(Paragraph("2. PROGRAM FEE STRUCTURE", h1_style))
    story.append(Paragraph(
        "The annual tuition fees and miscellaneous admin fees at GSIT are categorized by quotas and course lines as follows:",
        body_style
    ))
    
    # Fees table
    fee_data = [
        ["Course / Program", "Quota / Entry Type", "Tuition Fee (Per Annum)"],
        ["B.E. / B.Tech", "Government Quota (TNEA Counselling)", "Rs. 1,25,000"],
        ["B.E. / B.Tech", "Management Quota (Direct)", "Rs. 2,20,000"],
        ["M.E. / M.Tech", "All Categories (Regular Intake)", "Rs. 1,20,000 (Rs. 60,000 / semester)"],
        ["MBA / MCA", "All Categories (Regular Intake)", "Rs. 80,000"]
    ]
    
    t_fee = Table(fee_data, colWidths=[150, 200, 150])
    t_fee.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fee)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Additional Annual Administrative Fees:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Examination Fee:</b> Rs. 10,000 per annum (covers semester exam registrations and lab logs).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Development Fee:</b> Rs. 10,000 per annum (supports advanced campus infrastructure and software licenses).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Library & Sports Fee:</b> Rs. 5,000 per annum (includes online digital journals access and gym membership).",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 3. Scholarship Details
    story.append(Paragraph("3. SCHOLARSHIP SCHEMES AND WAIVERS", h1_style))
    story.append(Paragraph(
        "GSIT offers extensive financial aid programs to reward academic merit, promote athletics, and support underprivileged students:",
        body_style
    ))
    
    story.append(Paragraph("<b>Academic Merit Scholarships:</b>", h2_style))
    story.append(Paragraph(
        "• <b>95% & Above in 12th Grade:</b> Qualified students receive a <b>100% Tuition Fee Waiver</b> for their entire program duration.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>90% to 94.9% in 12th Grade:</b> Qualified students receive a <b>50% Tuition Fee Waiver</b>.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <i>Note:</i> To maintain this scholarship in subsequent years, students must maintain a CGPA of 8.5 or higher with no active backlogs.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Sports Merit Scholarships:</b>", h2_style))
    story.append(Paragraph(
        "• <b>National/International Representation:</b> Students who have represented the country at National or International level tournaments receive a <b>100% Tuition Fee Waiver</b>.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>State-Level Representation:</b> Students who have represented their state in recognized State-level tournaments receive a <b>50% Tuition Fee Waiver</b>.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>First Graduate Concession:</b>", h2_style))
    story.append(Paragraph(
        "• Candidates applying under Government Quota who are the first individuals in their families to pursue higher professional graduation are eligible for a tuition fee concession of <b>Rs. 25,000 per annum</b>, subsidized by the State Government.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Government Reserved Category Scholarships:</b>", h2_style))
    story.append(Paragraph(
        "• <b>SC/ST/SCA Candidates:</b> Full tuition fee reimbursement is provided for students whose annual family income is below Rs. 2.5 Lakhs.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>BC/MBC Candidates:</b> Post-matric scholarships are available for students whose annual family income is below Rs. 2.0 Lakhs.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 4. Required Documents
    story.append(Paragraph("4. REQUIRED DOCUMENTS FOR REGISTRATION", h1_style))
    story.append(Paragraph(
        "During physical counseling and registration at the Admissions Office (Admin Block, Ground Floor), candidates must submit their <b>original documents</b> along with <b>three sets of photocopies</b>:",
        body_style
    ))
    story.append(Paragraph("1. <b>10th Mark Sheet:</b> Secondary School Leaving Certificate (SSLC) original.", bullet_style))
    story.append(Paragraph("2. <b>12th Mark Sheet:</b> Higher Secondary Certificate (HSC) / Diploma mark sheets original.", bullet_style))
    story.append(Paragraph("3. <b>Transfer Certificate (TC):</b> Original certificate issued by the school/college last attended.", bullet_style))
    story.append(Paragraph("4. <b>Community Certificate:</b> Required for candidates claiming reservation quotas (OBC/BC/MBC/SC/ST).", bullet_style))
    story.append(Paragraph("5. <b>Income Certificate:</b> Mandatory for students applying for SC/ST scholarships or first graduate schemes.", bullet_style))
    story.append(Paragraph("6. <b>First Graduate Certificate:</b> Issued and digitally signed by the competent Tahsildar (if claiming the concession).", bullet_style))
    story.append(Paragraph("7. <b>Migration Certificate:</b> Required only for students belonging to non-state boards (CBSE, ICSE, or other state boards).", bullet_style))
    story.append(Paragraph("8. <b>Aadhaar Card:</b> Photocopy for identity and address verification.", bullet_style))
    story.append(Paragraph("9. <b>Recent Photos:</b> 5 recent passport-size color photographs.", bullet_style))
    story.append(Spacer(1, 10))
    
    # 5. Hostel Information
    story.append(Paragraph("5. HOSTEL AND RESIDENTIAL INFORMATION", h1_style))
    story.append(Paragraph(
        "GSIT offers fully furnished residential complexes on campus to provide students with a secure and collaborative environment:",
        body_style
    ))
    
    story.append(Paragraph("<b>Accommodation Options & Blocks:</b>", h2_style))
    story.append(Paragraph("• <b>Boys' Hostel:</b> Kaviri Block and Ganga Block.", bullet_style))
    story.append(Paragraph("• <b>Girls' Hostel:</b> Yamuna Block and Narmada Block.", bullet_style))
    story.append(Paragraph("• <b>Room Types:</b> Twin Sharing (AC & Non-AC), and Four Sharing (Non-AC).", bullet_style))
    
    story.append(Paragraph("<b>Hostel & Mess Fee Structure (Per Academic Year):</b>", h2_style))
    
    hostel_data = [
        ["Room Configuration", "Type", "Annual Fee (Room Rent + Mess Food)"],
        ["Double Sharing (Twin)", "Air Conditioned (AC)", "Rs. 1,20,000"],
        ["Double Sharing (Twin)", "Non-AC", "Rs. 95,000"],
        ["Quad Sharing (Four)", "Non-AC", "Rs. 85,000"],
        ["Security Deposit", "Refundable (One-Time)", "Rs. 5,000"]
    ]
    
    t_hostel = Table(hostel_data, colWidths=[150, 150, 200])
    t_hostel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_hostel)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hostel Rules, Timings, & Facilities:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Gate Closure Times:</b> The residential main gates close strictly at <b>7:30 PM for Girls</b> and <b>9:00 PM for Boys</b>. Permission for late entry is granted only under emergency circumstances with warden authorization.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Mess Hours:</b> Dining halls serve food during standard hours: Breakfast (7:00 AM - 8:30 AM), Lunch (12:00 PM - 1:30 PM), and Dinner (7:30 PM - 9:00 PM). Outside food ordering is permitted only on weekends.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Visitor Policy:</b> Parents and authorized guardians are allowed to meet residents in the main hostel lobbies from <b>4:30 PM to 6:30 PM</b> on weekdays. Visitors are not allowed inside individual student rooms.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Campus Facilities:</b> Residents enjoy high-speed 24/7 campus Wi-Fi (up to 100 Mbps), fully-equipped gymnasium spaces, study/discussion rooms, and a 24/7 Medical Center equipped with an ambulance located next to the physical education block.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 6. Examination Support
    story.append(Paragraph("6. EXAMINATION SUPPORT", h1_style))
    story.append(Paragraph(
        "The Controller of Examinations (CoE) office regulates all terminal testing, grade assessments, hall ticket downloads, and revaluation procedures for all registered engineering programs.",
        body_style
    ))
    
    story.append(Paragraph("<b>Exam Timetable (Sample Schedule Reference):</b>", h2_style))
    story.append(Paragraph(
        "Students can refer to the sample semester timetable schedule below for course exam distributions. Detailed department exam schedules are published 15 days before exams start.",
        body_style
    ))
    
    exam_timetable_data = [
        ["Date & Day", "Session & Time", "Course Code", "Subject / Course Title", "Sem"],
        ["15-Nov-2026", "FN (10 AM - 1 PM)", "CS8501", "Theory of Computation", "V"],
        ["17-Nov-2026", "FN (10 AM - 1 PM)", "CS8502", "Object Oriented Analysis & Design", "V"],
        ["19-Nov-2026", "AN (2 PM - 5 PM)", "EC8551", "Microprocessors & Microcontrollers", "V"],
        ["21-Nov-2026", "FN (10 AM - 1 PM)", "MA8551", "Algebra and Number Theory", "V"]
    ]
    
    t_exam = Table(exam_timetable_data, colWidths=[90, 110, 80, 180, 40])
    t_exam.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_exam)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hall Ticket Download & Eligibility:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Eligibility Criteria:</b> Hall tickets are released online. To download hall tickets, students must maintain a minimum of 75% attendance in each registered theory/practical course and clear all outstanding tuition and hostel fee dues.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Download Portal:</b> Eligible students must access the GSIT Student Portal, navigate to 'Downloads > Exam Hall Ticket', enter their Registration Number and Date of Birth, and download/print the ticket.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Discrepancies:</b> Any typing errors, missing subjects, or wrong photograph details on the hall ticket must be immediately reported to the CoE office at least 3 working days prior to the first exam.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Internal Marks & Assessment:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Assessment Weightage:</b> Internal assessment marks constitute 20% of the overall course grade. They are calculated based on three periodic Cycle Tests (each worth 50 marks, normalized to 15 marks total) and assignments/quizzes (5 marks).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Portal Verification:</b> Cumulative internal marks are updated on the GSIT Student Portal at the end of each Cycle Test. Students must check their marks and report any discrepancies to the class advisor within 3 working days.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Revaluation Process & Script Photocopy:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Answer Script Photocopy:</b> Students unsatisfied with their semester exam grades can apply for a photocopy of their evaluated answer script within 7 days of results declaration. The fee is Rs. 300 per paper.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Revaluation Application:</b> After reviewing the photocopy, students can apply for revaluation within 5 days of receiving the photocopy. The revaluation fee is Rs. 500 per paper, payable online.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Grade Revision:</b> If the revaluated score varies by more than 15% from the original score or results in a grade change, the updated grade will be published. Otherwise, the original grade remains final.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 7. Placement Cell Assistant
    story.append(Paragraph("7. CAREER GUIDANCE & PLACEMENT CELL ASSISTANT", h1_style))
    story.append(Paragraph(
        "The Career Guidance and Placement Cell at GSIT coordinates campus placement drives, internship acquisitions, industry collaborations, and soft skills training programs.",
        body_style
    ))
    
    story.append(Paragraph("<b>Placement Eligibility & Training:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Academic Eligibility:</b> Students must maintain a minimum CGPA of 6.5 with zero active/standing backlogs to participate in campus recruitment drives.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Training Requirement:</b> A minimum of 90% attendance in placement preparation bootcamps, mock interviews, and soft-skills sessions is mandatory to remain eligible for placement drives.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Company Requirements & Domains:</b>", h2_style))
    story.append(Paragraph(
        "• <b>IT & Software Services:</b> Require a minimum 60% aggregate (or 7.0 CGPA) throughout UG, strong proficiency in Data Structures, Algorithms, and Object-Oriented Programming, and clearing of coding tests.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Core Engineering Sectors:</b> Require core domain knowledge (e.g., VLSI, Embedded Systems, CAD/CAM) and a minimum of 6.5 CGPA with no history of standing backlogs.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Interview Schedule (Sample Drive Reference):</b>", h2_style))
    story.append(Paragraph(
        "Students can refer to the sample recruitment schedule below for upcoming campus drives. Detailed company schedules are emailed to registered candidates.",
        body_style
    ))
    
    placement_schedule_data = [
        ["Date & Day", "Company Name", "Target Branches", "Venue / Mode", "Reporting Time"],
        ["05-Oct-2026", "GlobalTech Solutions", "CSE, IT, ECE", "Main Seminar Hall", "08:30 AM"],
        ["08-Oct-2026", "AeroSpace Tech Corp", "Mech, EEE, ECE", "Block III Seminar Hall", "09:00 AM"],
        ["12-Oct-2026", "Nova Software Systems", "All UG / PG", "Online (Virtual)", "10:00 AM"],
        ["15-Oct-2026", "Quant Analytics Labs", "CSE, IT (Min 7.5 CGPA)", "Lab 4, CSE Block", "08:30 AM"]
    ]
    
    t_placement = Table(placement_schedule_data, colWidths=[90, 120, 110, 110, 70])
    t_placement.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_placement)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Resume Guidelines & Formats:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Official Template:</b> Resumes must follow the standard single-page LaTeX template provided by the Placement Cell. Multi-page resumes are strictly not allowed.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Verification:</b> All information listed (CGPA, marks, project works, and internship experience) must be verified and signed off by the Department Placement Coordinator before submission.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Internship Opportunities:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Target Candidates:</b> 3rd and 4th-year students are eligible for summer/winter internships with durations between 2 to 6 months.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Academic Credits & Stipend:</b> Internships can be converted into 2 to 3 academic credits under the autonomous curriculum, subject to submitting the final project report and a stipend certificate.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    # 8. Faculty Support
    story.append(Paragraph("8. FACULTY ADMINISTRATIVE & SUPPORT INFORMATION", h1_style))
    story.append(Paragraph(
        "This section details administrative guidelines, academic calendars, and exam duties assigned to the faculty members of GSIT.",
        body_style
    ))
    
    story.append(Paragraph("<b>Faculty Leave Policies:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Casual Leave (CL):</b> Full-time faculty members are entitled to 12 days of Casual Leave per calendar year. A maximum of 3 consecutive days of CL can be availed at a time.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Duty Leave (DL):</b> Granted up to 10 days per academic year for attending conferences, presenting research papers, or acting as external examiners in other institutions.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Medical Leave (ML):</b> Eligible for up to 10 days of ML per year. A valid medical certificate must be submitted to the HR desk for leaves exceeding 3 days.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Approval Procedure:</b> All leave requests must be submitted online via the Faculty Portal and approved by the HOD at least 2 days in advance, except in emergency cases.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>Academic Calendar (Sample Reference):</b>", h2_style))
    story.append(Paragraph(
        "Faculty members and students can refer to the sample academic calendar details below for planning activities.",
        body_style
    ))
    
    academic_calendar_data = [
        ["Month", "Dates", "Academic Event / Milestone Target", "Details / Audience"],
        ["August 2026", "03-Aug-2026", "Commencement of Classes (Odd Sem)", "All UG & PG Students"],
        ["September 2026", "07 to 11 Sep", "Cycle Test I Examinations", "All UG & PG Courses"],
        ["October 2026", "19 to 23 Oct", "Cycle Test II Examinations", "All UG & PG Courses"],
        ["November 2026", "02 to 07 Nov", "End Semester Practical Examinations", "Laboratory Courses"],
        ["November 2026", "12-Nov-2026", "Commencement of End Sem Theory Exams", "CoE Office Regulation"]
    ]
    
    t_calendar = Table(academic_calendar_data, colWidths=[90, 100, 190, 120])
    t_calendar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_calendar)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Examination Duties & Guidelines:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Invigilation Duty Slots:</b> Every faculty member is assigned a minimum of 6 invigilation slots per semester by the Exam Cell. Attendance is mandatory.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Reporting Time:</b> Assigned invigilators must report to the CoE control room 30 minutes prior to the examination start time (FN: 09:30 AM, AN: 01:30 PM).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Evaluation Timelines:</b> Senior faculty members may be appointed to the Flying Squad. Standard centralized answer script evaluation must be completed within 10 days of the respective subject examinations.",
        bullet_style
    ))
    story.append(Spacer(1, 10))
    
    doc.build(story)
    print(f"Admissions PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    output = "uploads/admission_support_system.pdf"
    if len(sys.argv) > 1:
        output = sys.argv[1]
    
    generate_pdf(output)
