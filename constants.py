ISSUE_US = 'US'
ISSUE_GSC = 'GSC'
ISSUE_EXEC = 'Exec'
ISSUE_CLASSPRES = 'ClassPres'
ISSUE_SPECFEE = 'SF'

ISSUE_TYPES = [
    (ISSUE_US, 'Undergrad Senate'),
    (ISSUE_GSC, 'Grad Student Council'),
    (ISSUE_CLASSPRES, 'Undergrad Class President'),
    (ISSUE_EXEC, 'Exec'),
    (ISSUE_SPECFEE, 'Special Fee request'),
]

SMSA_OFFICES = (
    ('SMSA-P', 'SMSA President'),
    ('SMSA-VP', 'SMSA Vice President'),
    ('SMSA-S', 'SMSA Secretary'),
    ('SMSA-T', 'SMSA Treasurer'),
    ('SMSA-ClassRep', 'SMSA Class Rep'),
    ('SMSA-SocChair', 'SMSA Class Social Chair'),
    ('SMSA-CCAP', 'SMSA CCAP Rep'),
    ('SMSA-PC', 'SMSA Policy Chair'),
    ('SMSA-AC', 'SMSA Advocacy Chair'),
    ('SMSA-MC', 'SMSA Mentorship Chair'),
)

ISSUE_TYPES.extend(SMSA_OFFICES)

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
    ('AtLarge', 'At-Large')
)

# ELECTORATES = [
#     ('ASSU-UG-1', 'Freshman'),
#     ('ASSU-UG-2', 'Sophomore'),
#     ('ASSU-UG-3', 'Junior'),
#     ('ASSU-UG-4', 'Senior'),
#     ('ASSU-UG', 'Undergrad'),
#     ('ASSU-Coterm', 'Coterm'),
#     ('ASSU-Grad', 'Grad'),
#     
#     # SMSA
#     ('Med', 'SMSA'),
#     ('Med-2', 'SMSA 2nd year'),
#     ('Med-3', 'SMSA 3rd year'),
#     ('Med-4', 'SMSA 4th year'),
#     ('Med-5+', 'SMSA 5th year and above'),
#     ('Med-PC', 'SMSA Pre-clinical'),
#     ('Med-C', 'SMSA Clinical'),
#     ('Med-MDPhD', 'SMSA MD-PhD'),
# ]

# ELECTORATES.extend(GSC_DISTRICTS)

VOTES_YNA = (
    (0, 'Abstain'),
    (1, 'No'),
    (2, 'Yes'),
)
