"""
Curated seed list of Dominican Republic fitness coaches.
Sourced via web research — all accounts verified as DR-based.

To expand: search Instagram/TikTok for #fitnessrd #coachrd #nutricionrd #entrenadorrd
"""

COACHES = [
    {
        "name": "Eddy Pilier",
        "instagram": "eddypilier",
        "tiktok": None,
        "website": None,
        # 25+ years experience, CEO of EP Fitness Studio, verified account
    },
    {
        "name": "RH Fitness Coach",
        "instagram": "rh_fitnesscoach",
        "tiktok": None,
        "website": None,
        # Nutrition + personalized plans, WhatsApp 829-977-8546
    },
    {
        "name": "Strength Fitness RD",
        "instagram": "strengthfitnessrd",
        "tiktok": None,
        "website": None,
        # Personal training + nutrition + supplements, WhatsApp 829-222-9143
    },
    {
        "name": "David Soto",
        "instagram": "davidsoto91",
        "tiktok": None,
        "website": None,
        # Entrenador Personal, Punta Cana / Gold's Gym
    },
    {
        "name": "Dairo Rojas",
        "instagram": "dairo9292",
        "tiktok": None,
        "website": None,
        # Certified NSPC + Performance PT Level 2, Strength & Hypertrophy 🇩🇴
    },
    {
        "name": "Gerald Castillo (FlacoFit)",
        "instagram": "flacofit.rd",
        "tiktok": None,
        "website": None,
        # International Certified Coach, based in R.D.
    },
    {
        "name": "Gustavo Dipres",
        "instagram": "gustavo_dipres",
        "tiktok": None,
        "website": None,
        # Nutrition coach, online + presencial, Fitness Champion
    },
    {
        "name": "Ariel Marmolejos",
        "instagram": "arielmv_coach",
        "tiktok": None,
        "website": None,
        # Fitness Coach, Santo Domingo 🇩🇴
    },
    {
        "name": "Coach Nathanael Rodriguez",
        "instagram": "coachnathanaelrodriguez",
        "tiktok": None,
        "website": None,
        # Personal + online coaching, La Vega RD, runs Exclusive Training Center
    },
    {
        "name": "Randi De Los Santos (Cirujano Fitness)",
        "instagram": "cirujano_fitness",
        "tiktok": None,
        "website": None,
        # Master Coach + Mentor, 10+ years, national/international athletes
    },
    {
        "name": "Gunter Gil Pelletier",
        "instagram": "guntergil",
        "tiktok": None,
        "website": None,
        # 3x Mr. Republica Dominicana, Founder FDFF & ADEPC, gym consultant
    },
    {
        "name": "Juan Carlos Simo",
        "instagram": "jc_simo",
        "tiktok": None,
        "website": None,
        # Psychologist + Functional Dietitian + Strength Coach, DR
    },
    {
        "name": "Jorge Moises Ramos",
        "instagram": "jmramos71",
        "tiktok": None,
        "website": None,
        # Trainer & Coach, 35+ years in fitness, DR
    },
    {
        "name": "Humberto Castrillon (Beto IFBB Pro)",
        "instagram": "beto_ifbbpro",
        "tiktok": None,
        "website": None,
        # IFBB Pro, online coach, Santo Domingo
    },
    {
        "name": "Anthony Marlon Perez",
        "instagram": "anthonypthebeast",
        "tiktok": None,
        "website": None,
        # Santo Domingo, fitness content
    },
    {
        "name": "EP Fitness Studio",
        "instagram": "epfitnesstudio.rd",
        "tiktok": None,
        "website": None,
        # Eddy Pilier's studio, women's training focus, Santo Domingo
    },
    {
        "name": "Exclusive Training Center",
        "instagram": "exclusive_training_center",
        "tiktok": None,
        "website": None,
        # La Vega RD — personal + group + online + domicilio training, 24/7 follow-up
    },
    {
        "name": "Sencillo Fit",
        "instagram": "sencillo_fit",
        "tiktok": None,
        "website": None,
        # DR fitness community figure
    },
    {
        "name": "Locura Fitness RD",
        "instagram": "locurafitnessrd",
        "tiktok": None,
        "website": None,
        # DR fitness media/magazine — industry insights
    },
    {
        "name": "Issaa Fit",
        "instagram": None,
        "tiktok": "issaafit",
        "website": None,
        # TikTok fitness coach, online coaching content
    },
]

# Convenience accessors used by collectors
INSTAGRAM_USERNAMES = [c["instagram"] for c in COACHES if c.get("instagram")]
TIKTOK_USERNAMES = [c["tiktok"] for c in COACHES if c.get("tiktok")]
WEBSITE_URLS = [(c["name"], c["website"]) for c in COACHES if c.get("website")]

# Mapping instagram handle -> full coach entry (for joins in processors)
BY_INSTAGRAM = {c["instagram"]: c for c in COACHES if c.get("instagram")}
BY_TIKTOK = {c["tiktok"]: c for c in COACHES if c.get("tiktok")}
