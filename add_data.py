from app import create_app, db
from app.models import User, Bibliography

app = create_app()

with app.app_context():
    # Create a user
    user = User(username='aoukarroum', email='aoukarroum@um6p.com')
    user.set_password('aoukarroum')
    db.session.add(user)
    db.session.commit()
    
    # Create a bibliography for the user
    biblio_content = """Overview

    What is the researcher best known for?
    Abdallah Oukarroum is best known for his research in plant physiology, stress responses, and environmental impact on agriculture.
    The fields of study they are best known for.
    Plant physiology, Environmental sciences, Agriculture
    Main research concerns and frequent connections to adjacent fields.
    The impact of environmental stressors on plant health, particularly drought and heavy metals, and the development of methods to mitigate these effects.
    Most Cited Work

    Chlorophyll a fluorescence as a tool to monitor physiological status of plants under stress conditions, Acta Physiologiae Plantarum, 2016 - 910 citations.
    Probing the responses of barley cultivars (Hordeum vulgare L.) to water deficit, Environmental and Experimental Botany, 2007 - 421 citations.
    Identification of nutrient deficiency in maize leaves using hyperspectral data, Plant Physiology and Biochemistry, 2014 - 344 citations.
    Inhibitory effects of silver nanoparticles in aquatic environments, Ecotoxicology and Environmental Safety, 2012 - 321 citations.
    Drought stress effects on photosystem I content and activity in barley leaves, Physiologia Plantarum, 2009 - 261 citations.
    Main Themes of Work
    Abdallah Oukarroum's research primarily revolves around the physiological responses of plants to environmental stressors, including drought and heavy metals. He frequently integrates knowledge from environmental sciences and agricultural practices to explore and propose mitigation strategies. His work includes examining the effects of various stressors on plant health and productivity, and developing methods to assess and improve plant resilience.

    Recent Work Highlights (last 5 years)

    Sequential co-processing of olive mill wastewater and livestock manure using composting technology, Process Safety and Environmental Protection, 2024 - 1 citation.
    Impact and toxicity of heavy metals on human health and the environment, International Journal of Environmental Science and Technology, 2024 - 2 citations.
    Advances in controlled release fertilizers: Concept, application, and future directions, Journal of Controlled Release, 2021 - 128 citations.
    Recent progress on emerging technologies for the treatment of municipal and industrial wastewater, Science of the Total Environment, 2021 - 27 citations.
    Composting date palm residues promotes circular economy and sustainable agriculture, Bioresource Technology, 2020 - 48 citations.
    Publication Fields
    Abdallah Oukarroum's publications are distributed across various fields, with notable frequency in the following journals:

    Science of the Total Environment (5 publications)
    Water, Air, and Soil Pollution (4 publications)
    Plant Physiology and Biochemistry (4 publications)
    Environmental and Experimental Botany (4 publications)
    Scientific Reports (3 publications)"""
    
    biblio = Bibliography(title='Sample Bibliography', content=biblio_content, author=user)
    db.session.add(biblio)
    db.session.commit()