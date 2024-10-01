from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Bibliography
from elsapy.elsclient import ElsClient
from elsapy.elssearch import ElsSearch
from elsapy.elsprofile import ElsAuthor
from elsapy.elsdoc import AbsDoc
import warnings
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

# Ensure environment variables are set
os.environ["AZURE_OPENAI_API_KEY"] = "a58855509b504f28a0c36a312f911ca5"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://openai-marjane.openai.azure.com/"
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o-marjane"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-07-01-preview"

warnings.filterwarnings('ignore')

llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

template = """
You are provided with a list of publications for a faculty member containing information about multiple papers authored by faculty members of UM6P. The list includes the following columns: Author, Title, Year of Publication, and Journal Name. Use this data to create a detailed scientific profile for each faculty member. The profile should include the following sections and adhere strictly to the specified format. Do not include any introductory or explanatory text, and do not mention the list or its columns. Directly generate the profiles in the format provided below, without adding any additional context or information.
Example 1: Name : Almotasembellah Abushaban
Almotasembellah Abushaban's research portfolio extensively covers various aspects of water treatment, desalination, and sustainable resource management. His work focuses on developing advanced methods to monitor and mitigate biofouling in seawater reverse osmosis (SWRO) systems, optimizing the reuse of waste materials as adsorbents, and addressing the broader challenges of water scarcity.
Biofouling Monitoring and Mitigation in SWRO Systems: A significant portion of Abushaban's research is dedicated to understanding and mitigating biofouling in seawater reverse osmosis systems. His studies on ATP measurement in seawater reverse osmosis systems explore filtration-based methods to eliminate seawater matrix effects, providing a more accurate assessment of biofouling potential. This work is critical for improving the operational efficiency and longevity of SWRO membranes. Abushaban has also developed and applied ATP-based bacterial growth potential methods to monitor biofouling in SWRO pre-treatment systems. These methods enable real-time assessment of bacterial activity, allowing for timely interventions to prevent biofouling. His research on pre-coating ultrafiltration membranes with iron hydroxide particles to limit non-backwashable fouling during seawater algal blooms further demonstrates innovative approaches to fouling control.
Sustainable Utilization of Waste Materials: Abushaban's research also addresses the sustainable re-utilization of waste materials as adsorbents for water and wastewater treatment. His studies highlight recent advancements and identify research gaps in using waste materials for adsorption, emphasizing the potential for these materials to improve water quality in emerging economies. By promoting the reuse of waste materials, his work supports the development of sustainable water treatment technologies.
Desalination and Water Scarcity Solutions: Exploring the potential of desalination as a solution to freshwater scarcity in developing countries is another key area of Abushaban's research. His work examines the feasibility and challenges of implementing desalination technologies in resource-limited settings, providing guidelines and assessment methods for membrane-based desalination. By addressing the technical and economic aspects of desalination, his research contributes to developing practical solutions for global water scarcity.
Advanced Analytical Methods and Fouling Indices: Abushaban has extensively utilized advanced analytical methods to predict and manage fouling in water treatment systems. His development of the Modified Fouling Index (MFI-0.45) and the use of the MFI-UF method for predicting particulate fouling in full-scale reverse osmosis plants offer valuable tools for optimizing membrane performance. These methods enhance the ability to predict and mitigate fouling, thereby improving the efficiency and reliability of water treatment processes.
Natural Organic Matter Removal and Climate Change Impact: His research on the removal of natural organic matter (NOM) by adsorption and the characterization of treatment methods provides insights into managing NOM in water treatment. This work is particularly relevant in the context of climate change, which affects the composition and concentration of NOM in water sources. By developing effective treatment methods, Abushaban's research helps ensure safe and reliable drinking water supplies.
Anaerobic Membrane Bioreactors and Biogas Production Abushaban's work on the design and operational aspects of anaerobic membrane bioreactors (AnMBRs) focuses on efficient wastewater treatment and biogas production. This research highlights the dual benefits of AnMBRs in treating wastewater while generating renewable energy, supporting the development of sustainable and energy-efficient wastewater treatment technologies.
Conclusion Almotasembellah Abushaban's extensive research significantly advances the fields of water treatment, desalination, and sustainable resource management. His work on biofouling monitoring and mitigation, sustainable use of waste materials, and advanced analytical methods provides innovative solutions for improving water quality and addressing water scarcity. By integrating chemical engineering, environmental science, and sustainability principles, Abushaban's research supports the development of efficient and eco-friendly technologies for water and wastewater treatment, contributing to global efforts to ensure clean and accessible water for all.
Example 2: Name : Yassine Ait Brahim
Yassine Ait Brahim's research portfolio is characterized by his extensive work in climate science, hydrogeology, and environmental management, with a particular focus on the interactions between climate variability, groundwater dynamics, and human activities in arid and semi-arid regions. His interdisciplinary approach integrates advanced modeling techniques, isotopic analysis, and remote sensing to address critical challenges in water resource management and environmental sustainability.
Climate Variability and Teleconnections: A significant portion of Ait Brahim's research focuses on understanding the patterns and impacts of climate variability and teleconnections. His studies on regional and global teleconnection patterns governing rainfall in the Western Mediterranean, particularly in the Lower Sebou Basin, provide valuable insights into how large-scale atmospheric circulation patterns influence local precipitation regimes. This research is crucial for predicting and managing water resources in regions susceptible to climatic fluctuations. Ait Brahim has also contributed to the SISAL (Speleothem Isotopes Synthesis and Analysis) database, which documents stable isotope and trace element records from speleothems. This global resource enhances our understanding of past climate changes and their drivers. His work on the Asian summer monsoon and its teleconnections, based on Chinese speleothem δ18O records, further underscores his expertise in paleoclimate research and the importance of speleothems in reconstructing historical climate variability.
Groundwater Dynamics and Water Resource Management: Ait Brahim's research on groundwater dynamics in the Haouz Plain explores the interactions between vegetation, water, and climate data, providing critical information for sustainable groundwater management. His studies on groundwater level forecasting in data-scarce regions using remote sensing data, hydrological modeling, and machine learning offer innovative solutions for predicting groundwater availability and planning resource allocation. His work on assessing water quality and nitrate sources in the Massa catchment using δ15N and δ18O tracers highlights the impact of natural and anthropogenic factors on groundwater quality. This research is essential for developing strategies to mitigate contamination and ensure safe water supplies in agricultural regions.
Hydroclimate and Paleoclimate Research: Ait Brahim has extensively investigated hydroclimate variability and its linkage to solar forcing in the Western Mediterranean during the last millennium. His research on multi-decadal to centennial hydro-climate variability provides valuable insights into the natural drivers of climate change and their impacts on regional water resources. Additionally, his studies on the North Atlantic ice-rafting events and their influence on ocean and atmospheric circulation during the Holocene contribute to the broader understanding of historical climate dynamics. His work on speleothem records, including the timing and structure of the Younger Dryas event, offers critical data for reconstructing past climate changes and understanding the underlying mechanisms. These studies provide a long-term perspective on climate variability and its implications for future climate scenarios.
Environmental Management and Sustainability Ait Brahim's research also addresses the practical aspects of environmental management and sustainability. His assessment of climate and land use changes in the Souss-Massa river basin highlights the impacts of these factors on groundwater resources and provides recommendations for sustainable water management. His work on the application of decision support tools for water governance in water-stressed areas underscores the importance of integrating scientific data with policy-making to enhance resource management.
Isotopic and Geochemical Analysis: Isotopic and geochemical analyses are central to Ait Brahim's research. His studies on the isotopic signatures of snow water resources in the Moroccan High Atlas mountains contribute to understanding surface and groundwater recharge processes. Additionally, his research on the isotopic composition of meteoric waters in Morocco provides insights into moisture sources and the climatic controls on precipitation patterns.
Conclusion Yassine Ait Brahim's extensive research significantly advances the understanding of climate variability, groundwater dynamics, and environmental management in arid and semi-arid regions. His work on teleconnections, paleoclimate records, and isotopic analyses provides valuable data for predicting and managing water resources in the face of climatic and anthropogenic challenges. By integrating advanced modeling techniques, remote sensing, and geochemical analyses, Ait Brahim's research supports the development of sustainable strategies for water resource management and environmental conservation.
Instructions for Generating Profiles: Name a: Start with the professor's name.
Research Overview: Provide a brief overview of the professor's research focus, summarizing the major themes and areas of interest based on the provided publications. Use specific language to describe the research portfolio, mirroring the structure used in the examples.
Detailed Research Areas:
Specific Projects and Studies: Create detailed descriptions of key research projects and studies conducted by the professor, derived from the titles and journal names of the papers. Ensure the description emphasizes the significance and impact of the research, as shown in the examples. Innovations and Methodologies: Highlight specific innovative methods and techniques developed or employed by the professor, inferred from the content of the papers. Each method or innovation should be connected to a specific research area. Applications and Impact: Discuss the practical applications of their research findings and the broader impact on the field and society, based on the journal names and context of the publications. Follow the structure and style of the examples closely. Conclusion: Summarize the significance and contributions of the professor's research. This should reflect the overall impact of their work on advancing the field and provide insight into how their research supports broader efforts or challenges.
Use the structure and guidance provided to generate profiles directly from the list data without adding any extra information. Make sure the output mirrors the examples given, including the language style and level of detail.
Faculty Member's Name is {first_name} {last_name}
Here is the list of publications:
{pubs_list}
"""

apikey = '7762f59ce3b9cb9117c74958bab4202b'
client = ElsClient(apikey)

bp = Blueprint('routes', __name__)

def save_picture(form_picture):
    picture_fn = secure_filename(form_picture.filename)
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

def author_pubs(author_id, client):
    """
    Obtain publication list for a given Scopus author ID author_id.
    """
    doc_srch = ElsSearch(f'AU-ID({author_id})', 'scopus')
    doc_srch.execute(client, get_all=True)

    pubs = []
    for rslt in doc_srch.results:
        year = rslt['prism:coverDate'].split('-')[0]
        citedby = rslt['citedby-count']
        scopusid = rslt['dc:identifier'].split(':')[1]
        title = rslt['dc:title']
        jrnlname = rslt['prism:publicationName']
        pubs.append({'year': year, 'cited': citedby, 'scopusid': scopusid, 'title': title, 'jrnlname': jrnlname})

    return pubs

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('routes.dashboard'))
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user is None or not user.check_password(password):
#             flash('Invalid username or password')
#             return redirect(url_for('routes.login'))
#         login_user(user)
#         return redirect(url_for('routes.dashboard'))
#     return render_template('login.html')

@bp.route('/')
def root():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('routes.admin_bibliographies'))
        else:
            return redirect(url_for('routes.dashboard'))
    else:
        return redirect(url_for('routes.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Check if the current user is admin
        if current_user.is_admin:
            return redirect(url_for('routes.admin_bibliographies'))
        else:
            return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))
        
        login_user(user)
        
        if user.is_admin:
            return redirect(url_for('routes.admin_bibliographies'))
        else:
            return redirect(url_for('routes.dashboard'))

    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'image_file' in request.files:
            image_file = save_picture(request.files['image_file'])
            current_user.image_file = image_file
            db.session.commit()
            flash('Your image has been updated!')
    bibliographies = current_user.bibliographies.all()
    return render_template('dashboard.html', bibliographies=bibliographies, image_file=current_user.image_file)

@bp.route('/bibliography/new', methods=['GET', 'POST'])
@login_required
def new_bibliography():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        biblio = Bibliography(title=title, content=content, author=current_user)
        db.session.add(biblio)
        db.session.commit()
        flash('Your bibliography has been created!')
        return redirect(url_for('routes.dashboard'))
    return render_template('edit_bibliography.html')

@bp.route('/bibliography/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bibliography(id):
    biblio = Bibliography.query.get_or_404(id)
    if biblio.author != current_user:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        biblio.title = request.form['title']
        biblio.content = request.form['content']
        db.session.commit()
        flash('Your bibliography has been updated!')
        return redirect(url_for('routes.dashboard'))
    return render_template('edit_bibliography.html', biblio=biblio)

@bp.route('/bibliography/<int:id>/delete', methods=['POST'])
@login_required
def delete_bibliography(id):
    biblio = Bibliography.query.get_or_404(id)
    if biblio.author != current_user:
        return redirect(url_for('routes.dashboard'))
    db.session.delete(biblio)
    db.session.commit()
    flash('Your bibliography has been deleted!')
    return redirect(url_for('routes.dashboard'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@bp.route('/admin/bibliographies')
@login_required
def admin_bibliographies():
    if not current_user.is_admin: 
        return redirect(url_for('routes.dashboard'))

    bibliographies = Bibliography.query.all()
    return render_template('admin_bibliographies.html', bibliographies=bibliographies)

@bp.route('/admin/bibliography/<int:id>/validate', methods=['POST'])
@login_required
def validate_bibliography(id):
    if not current_user.is_admin:
        return redirect(url_for('routes.admin_bibliographies'))

    biblio = Bibliography.query.get_or_404(id)
    biblio.is_validated_by_admin = not biblio.is_validated_by_admin
    db.session.commit()
    flash(f'Bibliography "{biblio.title}" validation status updated!')
    return redirect(url_for('routes.admin_bibliographies'))

@bp.route('/bibliography/<int:id>/validate_faculty', methods=['POST'])
@login_required
def validate_bibliography_faculty(id):
    biblio = Bibliography.query.get_or_404(id)
    
    # Only the author (faculty) can validate
    if biblio.author != current_user:
        return redirect(url_for('routes.dashboard'))

    # Toggle validation by faculty
    biblio.is_validated_by_faculty = not biblio.is_validated_by_faculty
    db.session.commit()
    
    flash(f'Bibliography "{biblio.title}" validation status updated by Faculty!')
    return redirect(url_for('routes.dashboard'))


@bp.route('/search-faculties', methods=['GET', 'POST'])
@login_required
def search_faculties():
    if not current_user.is_admin:
        return redirect(url_for('routes.admin_bibliographies'))
    
    faculties = []
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Search in Scopus
        auth_srch = ElsSearch(f'AUTHLASTNAME({last_name}) AUTHFIRST({first_name})', 'author')
        auth_srch.execute(client)

        faculties = []
        for author in auth_srch.results:
            author_id = author['dc:identifier'].split(':')[1]
            first_name_scopus = author['preferred-name']['given-name']
            last_name_scopus = author['preferred-name']['surname']
            affil_name = author['affiliation-current']['affiliation-name']
            affil_id = author['affiliation-current']['affiliation-id']
            
            faculties.append({
                'first_name': first_name_scopus,
                'last_name': last_name_scopus,
                'author_id': author_id,
                'affil_id': affil_id,
                'affil_name': affil_name
            })
    
    return render_template('search_faculties.html', faculties=faculties)

@bp.route('/user/<int:user_id>/bibliographies', methods=['GET'])
@login_required
def view_user_bibliography(user_id):
    if not current_user.is_admin:
        return redirect(url_for('routes.dashboard'))

    user = User.query.get_or_404(user_id)
    bibliographies = Bibliography.query.filter_by(user_id=user_id).all()

    return render_template('dashboard.html', bibliographies=bibliographies, image_file=user.image_file)

@bp.route('/generate-report/<author_id>/<first_name>/<last_name>/<affil_name>', methods=['GET', 'POST'])
@login_required
def generate_report(author_id, first_name, last_name, affil_name):

    username = f"{first_name[0].lower()}{last_name.lower()}"
    email = f"{first_name.lower()}.{last_name.lower()}@cleverlytics.com"
    password = f"{first_name[0].lower()}{last_name.lower()}"


    publications = author_pubs(author_id, client)

    pubs_list = "\n".join([f"{pub['year']}: {pub['title']} ({pub['jrnlname']}, cited {pub['cited']} times)" for pub in publications])

    prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    template,
                )
            ]
        )

    chain = prompt | llm
    gpt_response = chain.invoke(
        {
            "pubs_list": pubs_list,
            "first_name": first_name.lower(),
            "last_name": last_name.lower()
        }
    ).content

    if request.method == 'POST':
        # Add a new user to the database
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create a bibliography for the user
        biblio_content = gpt_response
        biblio = Bibliography(title=f"{first_name} {last_name}", content=biblio_content, author=user)
        db.session.add(biblio)
        db.session.commit()

        # print(biblio_content)

        flash(f"New user '{username}' and bibliography created successfully!")
        return redirect(url_for('routes.admin_bibliographies'))
        # flash(f"biblio content : {biblio_content}")

    return render_template('generate_report.html', 
                           first_name=first_name, 
                           author_id=author_id,
                           last_name=last_name, 
                           affil_name=affil_name, 
                           username=username, 
                           email=email, 
                           password=password, 
                           bibliography=gpt_response)