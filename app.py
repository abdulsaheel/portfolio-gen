from flask import Flask, request, render_template, send_from_directory
import os
import imgbbpy

app = Flask(__name__)
PATH = os.path.dirname(__file__)

def upload_image(file):
    """
    Uploads an image to the ImgBB service and returns the image URL.

    Args:
        file: The uploaded file.

    Returns:
        str: The URL of the uploaded image.
    """
    client = imgbbpy.SyncClient('d0586c7100ba883281c4202897166142')  # Replace 'YOUR_API_KEY' with your actual ImgBB API key
    image = client.upload(file=file)
    print(f"Image uploaded successfully. URL: {image.url}")
    os.remove(file)
    return image.url

@app.route('/submit', methods=['POST'])
def submit():
    contact_content = ''
    # Set a default value for portrait_url
    portrait_url = ''

    # Inside the submit function
    if 'image' in request.files:
        image_file = request.files['image']
        print(f"Received image file: {image_file.filename}")
        # Check if the file is allowed
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if image_file.filename and '.' in image_file.filename and image_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Save the image temporarily (optional)
            temp_directory = os.path.join(PATH, 'temp')
            if not os.path.exists(temp_directory):
                os.makedirs(temp_directory)
            image_path = os.path.join(PATH, 'temp', image_file.filename)
            image_file.save(image_path)

            # Upload the image to ImgBB and get the image URL
            portrait_url = upload_image(image_path)
            print(portrait_url)

    fname = request.form['fname']
    lname = request.form['lname']
    roll_no = request.form['roll_no']
    description = request.form['description']
    experience_num = int(request.form['experience_num'])
    experience_content = ''
    for i in range(experience_num):
        experience_title = request.form[f'experience_title_{i}']
        experience_duration = request.form[f'experience_duration_{i}']
        experience_description = request.form[f'experience_description_{i}']
        experience_content += f'<li>\n<h3>{experience_title}</h3>\n<h4 class="lead">{experience_duration}</h4>\n<p>{experience_description}</p>\n</li>\n'

    # Calculate the number of rows needed based on the number of projects per row (e.g., 3 projects per row)
    project_num = int(request.form['project_num'])
    projects_per_row = 3
    project_rows = (project_num + projects_per_row - 1) // projects_per_row
    project_content = ''

    for i in range(project_rows):
        project_content += '<div class="row text-center">\n'

        for j in range(projects_per_row):
            index = i * projects_per_row + j

            if index < project_num:
                project_title = request.form[f'project_title_{index}']
                project_description = request.form[f'project_description_{index}']
                project_url = request.form[f'project_url_{index}']

                project_content += f'''
                    <div class="col-md-4 my-2">
                        <div class="card">
                            <div class="card-body">
                                <h3 class="card-title">{project_title}</h3>
                                <p class="card-text lead">{project_description}</p>
                                <a href="{project_url}" target="_blank" class="btn btn-primary">Check it out</a>
                            </div>
                        </div>
                    </div>
                '''

    contact_email = request.form['contact_email']
    contact_linkedin = request.form.get('contact_linkedin', '')
    contact_phone = request.form['contact_phone']
    contact_github = request.form.get('contact_github', '')
    contact_twitter = request.form.get('contact_twitter', '')

    # Generate contact content based on the provided details
    contact_content = ''
    if contact_email:
        contact_content += f'<li><a href="mailto:{contact_email}" target="_blank"><i class="bi bi-envelope me-3"></i></a></li>\n'
    if contact_linkedin:
        contact_content += f'<li><a href="{contact_linkedin}" target="_blank"><i class="bi bi-linkedin me-3"></i></a></li>\n'
    if contact_github:
        contact_content += f'<li><a href="{contact_github}" target="_blank"><i class="bi bi-github me-3"></i></a></li>\n'
    if contact_twitter:
        contact_content += f'<li><a href="{contact_twitter}" target="_blank"><i class="bi bi-twitter me-3"></i></a></li>\n'

    # Extract skills, education, and certification data from the form
    skills = request.form.getlist('skills')
    education = request.form.getlist('education')
    certification = request.form.getlist('certification')

    # Generate content for skills, education, and certification sections
    skills_content = ''
    for skill in skills:
        skills_content += f'<li>{skill}</li>\n'
    # Extract education data from form
    education_degrees = request.form.getlist('education_degrees')
    education_schools = request.form.getlist('education_schools')
    education_durations = request.form.getlist('education_durations')

    # Generate education content based on the provided details
    education_content = ''
    for degree, school, duration in zip(education_degrees, education_schools, education_durations):
        education_content += f'<div class="education-item alert alert-success" role="alert">\n'
        education_content += f'    <li>{degree} - {school} ({duration})</li>\n'
        education_content += f'</div>\n'

    # Extract certification data from form
    certification_names = request.form.getlist('certification_names')
    certification_organizations = request.form.getlist('certification_organizations')
    certification_dates = request.form.getlist('certification_dates')

    # Generate certification content based on the provided details
    certification_content = ''
    for name, organization, date in zip(certification_names, certification_organizations, certification_dates):
        certification_content += f'<div class="certification-item alert alert-info" role="alert">\n'
        certification_content += f'    <li>{name} - {organization} ({date})</li>\n'
        certification_content += f'</div>\n'

    # Check if the user wants to use default colors
    use_default_colors = 'use_default_colors' in request.form
    # Extract skill data from form
    # Extract skill data from form, including descriptions
    skill_names = request.form.getlist('skills')
    skill_levels = request.form.getlist('skill_levels')
    skill_descriptions = request.form.getlist('skill_descriptions')

    # Generate skill content based on the provided details
    skills_content = ''
    for name, level, skill_descriptions in zip(skill_names, skill_levels, skill_descriptions):
        skills_content += f'<div class="skill-item card">\n'
        skills_content += f'    <li class="list-group-item">{name} - {level} - {skill_descriptions}</li>\n'
        skills_content += f'</div>\n'

    # Set default colors if selected or get values from the form
    body_primary = '#343a40' if use_default_colors else request.form.get('body_primary', '')
    bg_primary = '#FFFFF0' if use_default_colors else request.form.get('bg_primary', '')
    bg_secondary = '#F1E4D1' if use_default_colors else request.form.get('bg_secondary', '')
    header_primary = '#7373FF' if use_default_colors else request.form.get('header_primary', '')
    header_secondary = '#3479d3' if use_default_colors else request.form.get('header_secondary', '')
    nav_accent = '#F0F0FF' if use_default_colors else request.form.get('nav_accent', '')
    hover = '#7373FF' if use_default_colors else request.form.get('hover', '')
    accent = '#FF6FB7' if use_default_colors else request.form.get('accent', '')
    content = f'''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <title>{fname} {lname}'s Portfolio</title>
        </head>
        <!--CSS styling-->
        <style>
         .certification-item {{
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        background-color: #f8f9fa; /* Bootstrap default background color */
    }}
            /*General shit*/
            :root{{
                --body-primary: {body_primary};
                --bg-primary: {bg_primary};
                --bg-secondary: {bg_secondary};
                --header-primary: {header_primary};
                --header-secondary: {header_secondary};
                --nav-accent: {nav_accent};
                --hover: {hover};
                --accent: {accent};
            }}
            body{{
                transition: opacity 1.5s;
                background-color: var(--bg-primary);
                opacity: 0;
            }}
            p, a, h1, h2, h3, h4, h5, h6{{
                color: var(--body-primary);
            }}
            section{{
                /*height: 100vh;*/
                padding: 20px 0;
            }}
            .fadein{{
                opacity: 0;
            }}
            .heading{{
                color: var(--header-primary)
            }}
            .card-title{{
                color: var(--header-secondary)
            }}
            /*Navbar*/
            .navbar{{
                position: sticky;
                top: 0;
                width: 100%;
                background-color: transparent;
            }}
            .navbar ul{{
                text-align: center;
            }}
            .nav-item{{
                display: inline;
            }}
            .nav-item a{{
                transition: 0.5s;
                font-size: 1.5rem;
                text-decoration: none;
                color: var(--body-primary);
                border-bottom: 3px solid var(--nav-accent);
            }}
            .nav-item a:hover{{
                transition: 0.5s;
                border-bottom: 3px solid var(--hover);
            }}
            /*Waving animation*/
            .wave{{
                animation-name: wave-animation;
                animation-duration: 2s;
                animation-iteration-count: infinite;
                transform-origin: 70% 70%;
                display: inline-block;
            }}
            @keyframes wave-animation{{
                0% {{transform: rotate( 0.0deg)}}
                10% {{transform: rotate(14.0deg)}}
                20% {{transform: rotate(-8.0deg)}}
                30% {{transform: rotate(14.0deg)}}
                40% {{transform: rotate(-4.0deg)}}
                50% {{transform: rotate(10.0deg)}}
                60% {{transform: rotate( 0.0deg)}}
                100% {{transform: rotate( 0.0deg)}}
            }}
            /*Home section*/
            .about-me{{
                font-size: 1.5rem;
            }}
            .contact-items li{{
                display: inline-block;
            }}
            .contact-items a{{
                transition: 0.5s;
                text-decoration: none;
                font-size: 2rem;
                display: inline-block;
            }}
            .contact-items a:hover{{
                transition: 0.5s;
                color: var(--hover)
            }}
            .rounded-circle{{
                border: 3px solid var(--accent);
            }}
            /*Experience section*/
            #experience{{
                background-color: var(--bg-secondary);
            }}
            .experience-items li{{
                border-left: 5px solid var(--accent);
                padding-left: 20px;
            }}
            .experience-items li h3{{
                color: var(--header-secondary);
            }}
        </style>
        <!--Body of site-->
        <body onload="document.body.style.opacity='1'">
            <!--Navbar-->
            <div class="navbar justify-content-center">
                <ul class="m-0 p-0 list-unstyled text-unstyled">
                    <li class="nav-item mx-2">
                        <a href="#"><i class="bi bi-house-door"></i></a>
                    </li>
                    <li class="nav-item mx-2">
                        <a href="#experience"><i class="bi bi-hourglass"></i></a>
                    </li>
                    <li class="nav-item mx-2">
                        <a href="#projects"><i class="bi bi-code-slash"></i></a>
                    </li>
                </ul>
            </div>
            <!--Home section-->
            <section id="home" class="p-4">
                <div class="container">
                    <h1 class="mb-3 heading"><span class="wave">👋</span> Hi, my name is {fname} {lname}</h1>
                    <div class="row">
                        <div class="col-md-8">
                            <p class="lead about-me">{description}</p>
                            <ul class="contact-items list-unstyled">
                                {contact_content}<br>
                                Email: {contact_email}<br>
                                Phone: {contact_phone}<br>
                                <!-- Add any additional contact items here using the same structure -->
                            </ul>
                        </div>
                        <div class="col-md-4 text-center">
                            <img class="rounded-circle p-2" src="{portrait_url}" width="100px">
                        </div>
                    </div>
                </div>
            </section>
         <!-- Skills Section -->
            <section id="skills" class="p-4">
                <div class="container">
                    <h1 class="mb-3 heading">Skills</h1>
                    <ul class="skills-items m-0 p-0 list-unstyled">
                        {skills_content}
                    </ul>
                </div>
            </section>

            <!-- Education Section -->
            <section id="education" class="p-4">
                <div class="container">
                    <h1 class="mb-3 heading">Education</h1>
                    <ul class="education-items m-0 p-0 list-unstyled">
                        {education_content}
                    </ul>
                </div>
            </section>

            <!-- Certification Section -->
            <section id="certification" class="p-4">
                <div class="container">
                    <h1 class="mb-3 heading">Certifications</h1>
                    <ul class="certification-items m-0 p-0 list-unstyled">
                        {certification_content}
                    </ul>
                </div>
            </section>


            <!--Experience section-->
           {f'<section id="experience" class="p-4"> <div class="container"> <h1 class="mb-3 heading">Experience</h1> <ul class="experience-items m-0 p-0 list-unstyled"> {experience_content} </ul> </div> </section>' if experience_content else ''}
            
           {f'<section id="projects" class="p-4"> <div class="container"> <h1 class="mb-3 heading">Projects</h1> {project_content} </div> </section>' if project_content else ''}
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>
        </body>
    </html>
    '''

    with open(os.path.join('generated_templates', f'{fname}_{roll_no}.html'), 'wb') as f:
        f.write(content.encode())
    return render_template('success.html', fname=fname, roll_no=roll_no)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/portfolios/<fname>_<roll_no>')
def portfolio_template(fname, roll_no):
    directory = 'generated_templates'
    filename = f'{fname}_{roll_no}.html'
    return send_from_directory(directory, filename)

def get_multiple_fields(form, *field_prefixes):
    data = []
    for i in range(1, 10):  # Assuming a maximum of 10 entries, adjust as needed
        entry = {}
        for prefix in field_prefixes:
            field_name = f"{prefix}_{i}"
            value = form.getlist(field_name)  # Use getlist to get multiple values for the same field
            if value:
                entry[prefix] = value
        if entry:
            data.append(entry)
    return data


def get_dynamic_content(data, title):
    content = ''
    for i, entry in enumerate(data, start=1):
        content += f'<div class="{title.lower()}-entry">'
        content += f'<h3>{title} {i}:</h3>'
        for key, value in entry.items():
            content += f'<p><strong>{key}:</strong> {value}</p>'
        content += '</div>'
    return content



if __name__ == '__main__':
    app.run(debug=True)
