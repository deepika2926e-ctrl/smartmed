import logging
from sqlalchemy.orm import Session
from app.models.medicine_info import EducationalMedicine

logger = logging.getLogger(__name__)

SAMPLE_EDUCATIONAL_MEDICINES = [
    {
        "name": "Amoxicillin",
        "generic_name": "Amoxicillin",
        "brand_names": "Amoxil, Trimox, Moxatag",
        "category": "Antibiotic",
        "description": "Amoxicillin is a moderate-spectrum, bactericidal beta-lactam penicillin-class antibiotic used to treat a wide variety of bacterial infections.",
        "common_uses": "Used for bacterial chest infections (pneumonia, bronchitis), ear infections (otitis media), tonsillitis, sinusitis, urinary tract infections, and dental abscesses.",
        "mechanism_of_action": "Inhibits bacterial cell wall synthesis by binding to penicillin-binding proteins (PBPs), leading to lysis and destruction of susceptible bacteria.",
        "available_forms": "Oral capsules (250mg, 500mg), tablets (875mg), oral suspension (125mg/5ml, 250mg/5ml), chewable tablets.",
        "common_side_effects": "Mild diarrhea, nausea, vomiting, mild skin rash, headache, changes in taste.",
        "serious_side_effects": "Severe watery diarrhea containing blood or mucus (C. difficile colitis), signs of allergic anaphylaxis (hives, facial/tongue swelling, breathing difficulty), jaundice, persistent fever.",
        "precautions": "Notify your physician immediately if you have a known penicillin allergy, mononucleosis (glandular fever), kidney disease, or asthma. Complete the entire prescribed course even if symptoms resolve.",
        "drug_interactions": "May interact with methotrexate, probenecid, allopurinol, warfarin and oral anticoagulants, and oral typhoid vaccine.",
        "storage_instructions": "Store capsules and dry powder at room temperature (20°C to 25°C / 68°F to 77°F) away from moisture and direct heat. Reconstituted liquid suspension must be kept refrigerated and discarded after 14 days.",
        "general_usage_info": "Typically taken every 8 to 12 hours with a full glass of water. Can be taken with or without food; taking with food often reduces stomach upset.",
        "reference_sources": "NHS UK Medicines A-Z (Amoxicillin); U.S. National Library of Medicine (MedlinePlus #685001); DailyMed FDA Labels.",
        "disclaimer": "Educational Information Only: This summary is sourced from official public health monographs and is not personalized medical advice. Always consult your prescriber before making changes."
    },
    {
        "name": "Paracetamol (Acetaminophen)",
        "generic_name": "Paracetamol / Acetaminophen",
        "brand_names": "Tylenol, Panadol, Calpol, Mapap",
        "category": "Analgesic & Antipyretic",
        "description": "A widely used non-opioid pain reliever and fever reducer for mild-to-moderate pain and febrile conditions.",
        "common_uses": "Headaches, migraines, muscle aches, toothache, back pain, osteoarthritis discomfort, menstrual cramps, cold/flu fever.",
        "mechanism_of_action": "Acts primarily in the central nervous system to inhibit prostaglandin synthesis and modulates endogenous cannabinoid/serotonergic pathways; reduces fever via action on the hypothalamic heat-regulating center.",
        "available_forms": "Tablets (325mg, 500mg, 650mg ER), oral liquid/syrup (160mg/5ml), suppositories, IV infusion.",
        "common_side_effects": "Generally well tolerated at therapeutic doses. Mild nausea, dyspepsia, or rash may occur rarely.",
        "serious_side_effects": "Severe liver toxicity (hepatotoxicity) especially with overdose, severe cutaneous adverse reactions (Stevens-Johnson syndrome), dark urine, yellowing of skin or eyes (jaundice).",
        "precautions": "Never exceed 4,000 mg (4 grams) in 24 hours for adults (often lower: 2,000–3,000 mg if regular alcohol user or liver impairment). Check all OTC cough/cold combo products to avoid accidental doubling.",
        "drug_interactions": "Chronic heavy alcohol consumption, warfarin (regular high doses may increase INR), isoniazid.",
        "storage_instructions": "Store at controlled room temperature (15°C to 30°C) protected from moisture and light. Keep strictly out of reach of children.",
        "general_usage_info": "Adult dosage is usually 500mg to 1000mg every 4 to 6 hours as needed, with a minimum interval of 4 hours between doses.",
        "reference_sources": "MedlinePlus (Acetaminophen); NHS Health A to Z (Paracetamol); British National Formulary (BNF).",
        "disclaimer": "Educational Information Only: Consult your doctor or pharmacist if pain persists beyond 7 days or fever beyond 3 days."
    },
    {
        "name": "Metformin",
        "generic_name": "Metformin Hydrochloride",
        "brand_names": "Glucophage, Fortamet, Glumetza, Riomet",
        "category": "Antidiabetic (Biguanide)",
        "description": "First-line oral medication for the management of type 2 diabetes mellitus, also utilized in polycystic ovary syndrome (PCOS).",
        "common_uses": "Lowers blood glucose levels in type 2 diabetes; improves insulin sensitivity; adjunctive treatment in PCOS.",
        "mechanism_of_action": "Decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity by increasing peripheral glucose uptake and utilization.",
        "available_forms": "Immediate-release tablets (500mg, 850mg, 1000mg), extended-release (XR/ER) tablets (500mg, 750mg, 1000mg), oral solution.",
        "common_side_effects": "Abdominal discomfort, diarrhea, bloating, nausea, metallic taste in mouth, flatulence.",
        "serious_side_effects": "Lactic acidosis (rare but life-threatening: deep rapid breathing, severe fatigue, muscle aches, abdominal pain), vitamin B12 deficiency with prolonged use.",
        "precautions": "Contraindicated in severe renal impairment (eGFR < 30 mL/min). Must be withheld before iodinated radiocontrast imaging procedures and surgical interventions as advised by clinicians.",
        "drug_interactions": "Alcohol (increases lactic acidosis risk), cimetidine, furosemide, carbonic anhydrase inhibitors.",
        "storage_instructions": "Store at 20°C to 25°C (68°F to 77°F). Keep bottle tightly closed.",
        "general_usage_info": "Take with meals to minimize gastrointestinal upset. Swallow extended-release tablets whole; do not crush or chew.",
        "reference_sources": "American Diabetes Association Standards of Care; MedlinePlus (Metformin); NHS UK.",
        "disclaimer": "Educational Information Only: Requires regular monitoring of kidney function (eGFR) and blood glucose. Follow physician instructions strictly."
    },
    {
        "name": "Amlodipine",
        "generic_name": "Amlodipine Besylate",
        "brand_names": "Norvasc, Katerzia, Amvaz",
        "category": "Antihypertensive (Calcium Channel Blocker)",
        "description": "A long-acting dihydropyridine calcium channel blocker used to treat high blood pressure and coronary artery disease (angina).",
        "common_uses": "Hypertension (high blood pressure), chronic stable angina, vasospastic (Prinzmetal's) angina.",
        "mechanism_of_action": "Inhibits transmembrane influx of extracellular calcium ions into vascular smooth muscle and cardiac muscle, causing peripheral arterial vasodilation and decreased peripheral resistance.",
        "available_forms": "Oral tablets (2.5mg, 5mg, 10mg), oral suspension (1mg/ml).",
        "common_side_effects": "Peripheral edema (swelling of ankles or feet), dizziness, flushing, palpitations, fatigue, headache.",
        "serious_side_effects": "Severe hypotension, worsening of angina or myocardial infarction upon dose titration in severe coronary disease, severe allergic reaction.",
        "precautions": "Caution in patients with severe hepatic impairment or severe aortic stenosis. Do not discontinue abruptly without discussing with your doctor.",
        "drug_interactions": "Simvastatin (do not exceed 20mg simvastatin daily when co-administered), tacrolimus, cyclosporine, CYP3A4 inhibitors (ketoconazole, diltiazem).",
        "storage_instructions": "Store between 15°C and 30°C (59°F and 86°F) in a tight, light-resistant container.",
        "general_usage_info": "Usually taken once daily at the same time every day, with or without food. Peak blood-pressure-lowering effect occurs within 6 to 12 hours.",
        "reference_sources": "MedlinePlus (Amlodipine); NHS UK (Amlodipine); FDA Approved Prescribing Information.",
        "disclaimer": "Educational Information Only: Continue taking your blood pressure medication even if you feel completely fine, as high blood pressure often has no symptoms."
    },
    {
        "name": "Atorvastatin",
        "generic_name": "Atorvastatin Calcium",
        "brand_names": "Lipitor, Torvast",
        "category": "Lipid-Lowering Agent (Statin)",
        "description": "An HMG-CoA reductase inhibitor used to lower blood cholesterol levels and decrease the risk of cardiovascular events (heart attack, stroke).",
        "common_uses": "Hypercholesterolemia, prevention of cardiovascular disease in high-risk individuals, prevention of recurrent myocardial infarction.",
        "mechanism_of_action": "Competitively inhibits 3-hydroxy-3-methylglutaryl-coenzyme A (HMG-CoA) reductase, the rate-limiting enzyme in hepatic cholesterol biosynthesis, upregulating LDL receptors.",
        "available_forms": "Oral tablets (10mg, 20mg, 40mg, 80mg).",
        "common_side_effects": "Nasopharyngitis, joint pain (arthralgia), mild muscle ache, diarrhea, dyspepsia.",
        "serious_side_effects": "Rhabdomyolysis (severe unexplained muscle pain, tenderness, weakness accompanied by dark reddish-brown urine), elevated liver enzymes, jaundice.",
        "precautions": "Contraindicated in active liver disease and pregnancy/breastfeeding. Promptly report any unexplained muscle aches or fatigue.",
        "drug_interactions": "Grapefruit juice in large quantities, gemfibrozil, clarithromycin, cyclosporine, protease inhibitors, strong CYP3A4 inhibitors.",
        "storage_instructions": "Store at 20°C to 25°C (68°F to 77°F).",
        "general_usage_info": "Taken once daily at any time of day, with or without food, but should be taken at roughly the same hour daily.",
        "reference_sources": "AHA/ACC Cholesterol Clinical Guidelines; MedlinePlus (Atorvastatin); NHS UK.",
        "disclaimer": "Educational Information Only: Best paired with a heart-healthy diet and regular exercise as directed by your physician."
    },
    {
        "name": "Omeprazole",
        "generic_name": "Omeprazole",
        "brand_names": "Prilosec, Losec, Omesec",
        "category": "Gastrointestinal (Proton Pump Inhibitor)",
        "description": "A proton pump inhibitor (PPI) that decreases the amount of acid produced in the stomach.",
        "common_uses": "Gastroesophageal reflux disease (GERD), heartburn, gastric and duodenal ulcers, Zollinger-Ellison syndrome, H. pylori eradication therapy.",
        "mechanism_of_action": "Suppresses gastric acid secretion by specific inhibition of the H+/K+-ATPase enzyme system ('proton pump') at the secretory surface of the gastric parietal cell.",
        "available_forms": "Delayed-release capsules (10mg, 20mg, 40mg), delayed-release tablets, oral suspension packets.",
        "common_side_effects": "Headache, abdominal pain, constipation, flatulence, nausea, vomiting.",
        "serious_side_effects": "Clostridium difficile-associated diarrhea, hypomagnesemia with long-term use, increased bone fracture risk, subacute cutaneous lupus erythematosus.",
        "precautions": "Should generally be used at the lowest effective dose for the shortest duration necessary. Long-term use (>1 year) requires periodic medical review.",
        "drug_interactions": "Clopidogrel (decreases active metabolite formation), diazepam, warfarin, methotrexate, antiretrovirals (atazanavir), iron supplements.",
        "storage_instructions": "Store at 15°C to 30°C (59°F to 86°F) in a dry place protected from light.",
        "general_usage_info": "Best taken in the morning 30 to 60 minutes before breakfast. Swallow capsules whole without chewing or crushing.",
        "reference_sources": "MedlinePlus (Omeprazole); NHS Medicines Guide; FDA Drug Information.",
        "disclaimer": "Educational Information Only: Relieving symptoms does not preclude the presence of underlying gastric malignancy. Consult a specialist for persistent reflux."
    },
    {
        "name": "Salbutamol (Albuterol)",
        "generic_name": "Salbutamol / Albuterol Sulfate",
        "brand_names": "Ventolin, ProAir, Proventil, Salamol",
        "category": "Respiratory (Short-Acting Beta-2 Agonist)",
        "description": "A fast-acting bronchodilator used as a rescue inhaler for the rapid relief of bronchospasm.",
        "common_uses": "Acute asthma attacks, wheezing, shortness of breath in chronic obstructive pulmonary disease (COPD), prevention of exercise-induced bronchospasm.",
        "mechanism_of_action": "Stimulates beta-2 adrenergic receptors in bronchial smooth muscle, causing relaxation, bronchodilation, and increased airflow.",
        "available_forms": "Metered-dose inhaler (MDI 100mcg/puff or 90mcg/puff), nebulizer solution, oral syrup, dry powder inhaler.",
        "common_side_effects": "Fine tremor (especially hands), rapid heartbeat (tachycardia), nervousness, headache, muscle cramps.",
        "serious_side_effects": "Paradoxical bronchospasm (immediate wheezing after inhalation), arrhythmias, severe hypokalemia, chest pain.",
        "precautions": "If you find yourself needing your rescue inhaler more than twice a week for asthma symptoms, your underlying controller therapy may need review by your doctor.",
        "drug_interactions": "Non-selective beta-blockers (propranolol) may block bronchodilator effect, diuretics (may enhance hypokalemia), MAO inhibitors.",
        "storage_instructions": "Store between 15°C and 25°C. Keep canister away from heat, flame, or direct sunlight. Do not puncture or incinerate canister.",
        "general_usage_info": "Typically 1 to 2 puffs inhaled every 4 to 6 hours as needed for acute symptoms, or 2 puffs 15 minutes prior to exercise.",
        "reference_sources": "Global Initiative for Asthma (GINA) Guidelines; MedlinePlus (Albuterol Inhalation); NHS UK.",
        "disclaimer": "Educational Information Only: A rescue inhaler provides symptom relief but does not treat underlying airway inflammation. Always carry your rescue inhaler."
    },
    {
        "name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "brand_names": "Advil, Motrin, Nurofen, Brufen",
        "category": "NSAID (Nonsteroidal Anti-inflammatory Drug)",
        "description": "A nonsteroidal anti-inflammatory drug used to manage pain, reduce inflammation, and lower fever.",
        "common_uses": "Musculoskeletal pain, arthritis, dental pain, headache, menstrual pain (dysmenorrhea), fever reduction.",
        "mechanism_of_action": "Non-selectively inhibits cyclooxygenase enzymes (COX-1 and COX-2), decreasing the synthesis of pro-inflammatory prostaglandins.",
        "available_forms": "Oral tablets/caplets (200mg, 400mg, 600mg, 800mg), liquid gels, pediatric oral suspension (100mg/5ml), topical gel.",
        "common_side_effects": "Stomach irritation, indigestion, nausea, dizziness, mild edema.",
        "serious_side_effects": "Gastrointestinal bleeding/ulceration, cardiovascular thrombotic events (myocardial infarction, stroke), renal impairment, severe allergic reactions.",
        "precautions": "Avoid in patients with active peptic ulcer disease, severe heart failure, or severe kidney disease, and in third trimester of pregnancy.",
        "drug_interactions": "Aspirin, other NSAIDs, oral anticoagulants (warfarin), antihypertensives (ACE inhibitors/ARBs), lithium, SSRIs.",
        "storage_instructions": "Store at room temperature (20°C to 25°C / 68°F to 77°F) away from excess moisture.",
        "general_usage_info": "Take with meals or milk to minimize gastric upset. Adults: usually 200mg to 400mg every 4 to 6 hours as needed; maximum OTC daily dose is 1200mg unless under medical supervision.",
        "reference_sources": "MedlinePlus (Ibuprofen); NHS Choices; FDA Drug Safety Communications.",
        "disclaimer": "Educational Information Only: Use the lowest effective dose for the shortest possible duration. Not recommended for long-term unmonitored use."
    },
    {
        "name": "Sertraline",
        "generic_name": "Sertraline Hydrochloride",
        "brand_names": "Zoloft, Lustral",
        "category": "Antidepressant (SSRI)",
        "description": "A selective serotonin reuptake inhibitor (SSRI) used in the treatment of major depressive disorder, anxiety disorders, and obsessive-compulsive disorder.",
        "common_uses": "Major depressive disorder, panic disorder, obsessive-compulsive disorder (OCD), post-traumatic stress disorder (PTSD), social anxiety disorder, premenstrual dysphoric disorder.",
        "mechanism_of_action": "Selectively inhibits the presynaptic reuptake of serotonin (5-HT) in the central nervous system, enhancing serotonergic neurotransmission.",
        "available_forms": "Oral tablets (25mg, 50mg, 100mg), oral liquid concentrate (20mg/ml).",
        "common_side_effects": "Nausea, insomnia or drowsiness, tremor, dry mouth, diarrhea, sexual dysfunction, sweating.",
        "serious_side_effects": "Serotonin syndrome (confusion, agitation, hyperreflexia, hyperthermia), suicidal thoughts in children/young adults during initial weeks, hyponatremia.",
        "precautions": "Do not stop taking abruptly; discontinuation symptoms may occur. Therapeutic benefit usually develops over 2 to 6 weeks.",
        "drug_interactions": "MAO inhibitors (strict 14-day washout required), linezolid, St. John's wort, tramadol, triptans, NSAIDs (increased bleeding risk).",
        "storage_instructions": "Store at 20°C to 25°C (68°F to 77°F). Keep oral solution properly diluted before intake as instructed.",
        "general_usage_info": "Take once daily in either the morning or evening, consistently with or without food.",
        "reference_sources": "NICE Guidelines for Depression and Anxiety; MedlinePlus (Sertraline); NHS Mental Health Medicines.",
        "disclaimer": "Educational Information Only: Never cease this medication without a structured taper supervised by your mental health clinician."
    },
    {
        "name": "Levothyroxine",
        "generic_name": "Levothyroxine Sodium",
        "brand_names": "Synthroid, Levoxyl, Eltroxin, Tirosint",
        "category": "Thyroid Hormone Replacement",
        "description": "Synthetic form of the endogenous thyroid hormone tetraiodothyronine (T4), used to treat hypothyroidism.",
        "common_uses": "Hypothyroidism (underactive thyroid), pituitary TSH suppression in thyroid cancer management, goiter treatment.",
        "mechanism_of_action": "Provides exogenous T4 which is peripherally deiodinated into the active thyroid hormone T3, binding to thyroid receptor proteins in the cell nucleus to regulate metabolic processes.",
        "available_forms": "Oral tablets (ranging from 25mcg to 300mcg in color-coded strengths), oral solution, soft gelatin capsules.",
        "common_side_effects": "Rare when appropriately dosed. Over-replacement symptoms include palpitations, weight loss, tremor, heat intolerance, insomnia.",
        "serious_side_effects": "Cardiac arrhythmias, angina pectoris, accelerated bone loss (osteoporosis) from excessive dosage.",
        "precautions": "Requires routine monitoring of serum TSH levels (usually 6 to 8 weeks after dose changes). Brands should not be switched interchangeably without clinician awareness.",
        "drug_interactions": "Calcium carbonate, iron supplements, soy, aluminum hydroxide antacids (separate by at least 4 hours), cholestyramine, warfarin.",
        "storage_instructions": "Store at room temperature (20°C to 25°C) protected from light and moisture.",
        "general_usage_info": "Must be taken on an empty stomach with a full glass of plain water, at least 30 to 60 minutes before breakfast or coffee.",
        "reference_sources": "American Thyroid Association (ATA) Guidelines; MedlinePlus (Levothyroxine); BNF.",
        "disclaimer": "Educational Information Only: Lifelong replacement is typical for primary hypothyroidism. Take consistently at the exact same hour daily."
    },
    {
        "name": "Lisinopril",
        "generic_name": "Lisinopril",
        "brand_names": "Prinivil, Zestril",
        "category": "Antihypertensive (ACE Inhibitor)",
        "description": "An angiotensin-converting enzyme (ACE) inhibitor used for treating hypertension, congestive heart failure, and improving survival post-myocardial infarction.",
        "common_uses": "Hypertension, heart failure, adjunct in acute myocardial infarction, diabetic nephropathy.",
        "mechanism_of_action": "Inhibits ACE, blocking conversion of angiotensin I to the potent vasoconstrictor angiotensin II, decreasing aldosterone secretion and reducing vascular resistance.",
        "available_forms": "Oral tablets (2.5mg, 5mg, 10mg, 20mg, 30mg, 40mg), oral solution.",
        "common_side_effects": "Persistent dry cough, dizziness, headache, fatigue, excessive hypotension on initial dose.",
        "serious_side_effects": "Angioedema (swelling of face, lips, tongue, or larynx causing airway obstruction), hyperkalemia (high blood potassium), renal dysfunction.",
        "precautions": "Strictly contraindicated in pregnancy (teratogenic / fetal toxicity). Report facial swelling or breathing difficulty immediately.",
        "drug_interactions": "Potassium supplements, potassium-sparing diuretics (spironolactone), NSAIDs, lithium, sacubitril/valsartan.",
        "storage_instructions": "Store at 20°C to 25°C (68°F to 77°F) protected from moisture.",
        "general_usage_info": "Taken once daily at approximately the same time, with or without food. Drink adequate fluids to prevent dehydration.",
        "reference_sources": "MedlinePlus (Lisinopril); NHS Medicines A-Z; American College of Cardiology Guidelines.",
        "disclaimer": "Educational Information Only: Requires periodic blood tests for serum creatinine and electrolytes."
    },
    {
        "name": "Cetirizine",
        "generic_name": "Cetirizine Hydrochloride",
        "brand_names": "Zyrtec, Piriteze, Alleroff",
        "category": "Antihistamine (Second-Generation)",
        "description": "A second-generation, non-sedating (or low-sedating) histamine H1-receptor antagonist used for allergic symptoms.",
        "common_uses": "Allergic rhinitis (hay fever), seasonal and perennial allergies, chronic idiopathic urticaria (hives), allergic conjunctivitis.",
        "mechanism_of_action": "Competitively antagonizes peripheral H1 receptors, blocking histamine release and mitigating allergic vascular and pruritic responses with minimal CNS penetration.",
        "available_forms": "Tablets (5mg, 10mg), chewable tablets, oral syrup (5mg/5ml), disintegrating tablets.",
        "common_side_effects": "Mild drowsiness/somnolence (in some individuals), dry mouth, fatigue, headache, dizziness.",
        "serious_side_effects": "Severe allergic anaphylaxis, urinary retention, severe sedation when combined with central nervous system depressants.",
        "precautions": "Use caution when driving or operating machinery until individual tolerance is established. Reduce dose in moderate-to-severe renal impairment.",
        "drug_interactions": "Alcohol, sedatives, tranquilizers, other antihistamines, theophylline.",
        "storage_instructions": "Store at 20°C to 25°C (68°F to 77°F). Protect from excessive moisture.",
        "general_usage_info": "Adults usually take 10mg once daily or 5mg twice daily, with or without food.",
        "reference_sources": "MedlinePlus (Cetirizine); NHS UK (Cetirizine); European Medicines Agency (EMA).",
        "disclaimer": "Educational Information Only: Over-the-counter allergy management. Consult your allergist or physician if allergic symptoms persist."
    }
]

def seed_educational_medicines(db: Session):
    """Seed educational medicines if database table is empty."""
    try:
        count = db.query(EducationalMedicine).count()
        if count == 0:
            logger.info("Seeding educational medicine catalog...")
            for med_data in SAMPLE_EDUCATIONAL_MEDICINES:
                med = EducationalMedicine(**med_data)
                db.add(med)
            db.commit()
            logger.info(f"Successfully seeded {len(SAMPLE_EDUCATIONAL_MEDICINES)} educational medicines.")
    except Exception as e:
        logger.error(f"Error seeding educational medicines: {e}")
        db.rollback()
