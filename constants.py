ISSUE_US = 'US'
ISSUE_GSC = 'GSC'
ISSUE_EXEC = 'Exec'
ISSUE_CLASSPRES = 'ClassPres'
ISSUE_SPECFEE = 'SF'

ISSUE_TYPES = (
    (ISSUE_US, 'Undergrad Senate'),
    (ISSUE_GSC, 'Grad Student Council'),
    (ISSUE_CLASSPRES, 'Undergrad Class President'),
    (ISSUE_EXEC, 'Exec'),
    (ISSUE_SPECFEE, 'Special Fee request'),
)

ENROLLMENT_STATUSES = (
    ('U', 'Undergrad'),
    ('C', 'Coterm'),
    ('G', 'Grad'),
)

CLASS_YEAR_FRESHMAN = '1'
CLASS_YEAR_SOPHOMORE = '2'
CLASS_YEAR_JUNIOR = '3'
CLASS_YEAR_SENIOR = '4'
UNDERGRAD_CLASS_YEARS = (
    (CLASS_YEAR_FRESHMAN, 'Freshman'),
    (CLASS_YEAR_SOPHOMORE, 'Sophomore'),
    (CLASS_YEAR_JUNIOR, 'Junior'),
    (CLASS_YEAR_SENIOR, 'Senior'),
)

VOTES_YNA = (
    (0, 'Abstain'),
    (1, 'No'),
    (2, 'Yes'),
)

GSC_DISTRICTS = (
  ('GSB', 'School of Business'),
  ('EarthSci', 'School of Earth Sciences'),
  ('Edu', 'School of Education'),
  ('Eng', 'School of Engineering'),
  ('H&S-Hum', 'School of Humanities and Sciences, Humanities'),
  ('H&S-NatSci', 'School of Humanities and Sciences, Natural Sciences'),
  ('H&S-SocSci', 'School of Humanities and Sciences, Social Sciences'),
  ('Law', 'School of Law'),
  ('Med', 'School of Medicine'),
)