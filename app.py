import sklearn
import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import google.generativeai as gen_ai
import firebase
from requests.exceptions import HTTPError
from streamlit_js_eval import streamlit_js_eval


config = {
    'apiKey': "AIzaSyBZW3nwcMgWPPNsJ5Qh9cXwQTQxap94FMY",
  'authDomain': "diseaseprediction-bfa57.firebaseapp.com",
  'databaseURL': "https://diseaseprediction-bfa57-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "diseaseprediction-bfa57",
  'storageBucket': "diseaseprediction-bfa57.appspot.com",
  'messagingSenderId': "124102292855",
  'appId': "1:124102292855:web:c10fc0ccbea6b3d9c11d72",
  'measurementId': "G-VRKM07JMM7"
}

app = firebase.initialize_app(config)
auth = app.auth()

load_dotenv()

def creds_entered(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state["authenticated"] = True
        if st.button("Enter Dashboard"):
            authenticate_user()
        st.success("Authentication Successful")
    except HTTPError as e:
        st.error("Authentication failed. Invalid username or password.")
        st.session_state["authenticated"] = False
    


def login_page():
    st.title("Welcome to ML Health Prediction!")
    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

    if choice == 'Login':
        email = st.text_input('Email Address')
        password = st.text_input('Password', type = 'password')
        if st.button("Login"):
            creds_entered(email, password)
               
    else:
        email = st.text_input('Email Address')
        password = st.text_input('Password', type = 'password')
        
        if st.button('Create My Account'):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success('Account Created!')
                st.markdown('Please Login using your email and password')
                st.balloons()
            except HTTPError as e:
                st.error("Password Must Be Atleast 6 characters long")


def authenticate_user():
    if "authenticated" not in st.session_state:
        login_page()
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            login_page()
            return False


if authenticate_user():
    
    # Set page configuration
    #st.set_page_config(page_title="Health Assistant",layout="wide",page_icon="🧑‍⚕️")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    gen_ai.configure(api_key=GOOGLE_API_KEY)
    model = gen_ai.GenerativeModel('gemini-pro')

    def translate_role_for_streamlit(user_role):
        if user_role == "model":
            return "assistant"
        else:
            return user_role

    # Function to initialize chat session
    def initialize_chat_session():
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

    # Function to display chat history
    def display_chat_history():
        for message in st.session_state.chat_session.history:
            with st.chat_message(translate_role_for_streamlit(message.role)):
                st.markdown(message.parts[0].text)


    # Get the current working directory
    working_dir = os.getcwd()
    
    # getting the working directory of the main.py


    diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))

    heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))

    parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))



    # sidebar for navigation
    with st.sidebar:
        if st.button("Logout"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
        selected = option_menu('Multiple Disease Prediction System',

                            ['Health Assistant','Diabetes Prediction',
                                'Heart Disease Prediction',
                                'Parkinsons Prediction'],
                            menu_icon='hospital-fill',
                                icons=['person','activity', 'heart', 'person'],
                            default_index=0)
       

    # for chatbot
    
    if selected == 'Health Assistant':

        st.title("🧑‍⚕️ Health Assistant")
        st.text("Greetings!, This is your AI Health Assistant😊")
        # Initialize chat session when opening the menu
        initialize_chat_session()

        # Display the chat history
        display_chat_history()


        # Input field for user's message
        user_prompt = st.chat_input("Ask Health Assistant...")

        if user_prompt:
            # Add user's message to chat and display it
            st.chat_message("user").markdown(user_prompt)

            # Send user's message to Gemini-Pro and get the response
            gemini_response = st.session_state.chat_session.send_message(user_prompt)

            # Display Gemini-Pro's response
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
        
        


    # Diabetes Prediction Page
    if selected == 'Diabetes Prediction':

        # page title
        st.title('Diabetes Prediction using ML')

        # getting the input data from the user
        col1, col2, col3 = st.columns(3)

        with col1:
            Pregnancies = st.text_input('Number of Pregnancies')

        with col2:
            Glucose = st.text_input('Glucose Level')

        with col3:
            BloodPressure = st.text_input('Blood Pressure value')

        with col1:
            SkinThickness = st.text_input('Skin Thickness value')

        with col2:
            Insulin = st.text_input('Insulin Level')

        with col3:
            BMI = st.text_input('BMI value')

        with col1:
            DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')

        with col2:
            Age = st.text_input('Age of the Person')


        # code for Prediction
        diab_diagnosis = ''

        # creating a button for Prediction

        if st.button('Diabetes Test Result'):

            user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                        BMI, DiabetesPedigreeFunction, Age]

            user_input = [float(x) for x in user_input]

            diab_prediction = diabetes_model.predict([user_input])

            if diab_prediction[0] == 1:
                diab_diagnosis = 'The person is diabetic'
            else:
                diab_diagnosis = 'The person is not diabetic'

        st.success(diab_diagnosis)

    # Heart Disease Prediction Page
    if selected == 'Heart Disease Prediction':

        # page title
        st.title('Heart Disease Prediction using ML')

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.text_input('Age')

        with col2:
            sex = st.text_input('Sex')

        with col3:
            cp = st.text_input('Chest Pain types')

        with col1:
            trestbps = st.text_input('Resting Blood Pressure')

        with col2:
            chol = st.text_input('Serum Cholestoral in mg/dl')

        with col3:
            fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl')

        with col1:
            restecg = st.text_input('Resting Electrocardiographic results')

        with col2:
            thalach = st.text_input('Maximum Heart Rate achieved')

        with col3:
            exang = st.text_input('Exercise Induced Angina')

        with col1:
            oldpeak = st.text_input('ST depression induced by exercise')

        with col2:
            slope = st.text_input('Slope of the peak exercise ST segment')

        with col3:
            ca = st.text_input('Major vessels colored by flourosopy')

        with col1:
            thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversable defect')

        # code for Prediction
        heart_diagnosis = ''

        # creating a button for Prediction

        if st.button('Heart Disease Test Result'):

            user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]

            user_input = [float(x) for x in user_input]

            heart_prediction = heart_disease_model.predict([user_input])

            if heart_prediction[0] == 1:
                heart_diagnosis = 'The person is having heart disease'
            else:
                heart_diagnosis = 'The person does not have any heart disease'

        st.success(heart_diagnosis)

    # Parkinson's Prediction Page
    if selected == "Parkinsons Prediction":

        # page title
        st.title("Parkinson's Disease Prediction using ML")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            fo = st.text_input('MDVP:Fo(Hz)')

        with col2:
            fhi = st.text_input('MDVP:Fhi(Hz)')

        with col3:
            flo = st.text_input('MDVP:Flo(Hz)')

        with col4:
            Jitter_percent = st.text_input('MDVP:Jitter(%)')

        with col5:
            Jitter_Abs = st.text_input('MDVP:Jitter(Abs)')

        with col1:
            RAP = st.text_input('MDVP:RAP')

        with col2:
            PPQ = st.text_input('MDVP:PPQ')

        with col3:
            DDP = st.text_input('Jitter:DDP')

        with col4:
            Shimmer = st.text_input('MDVP:Shimmer')

        with col5:
            Shimmer_dB = st.text_input('MDVP:Shimmer(dB)')

        with col1:
            APQ3 = st.text_input('Shimmer:APQ3')

        with col2:
            APQ5 = st.text_input('Shimmer:APQ5')

        with col3:
            APQ = st.text_input('MDVP:APQ')

        with col4:
            DDA = st.text_input('Shimmer:DDA')

        with col5:
            NHR = st.text_input('NHR')

        with col1:
            HNR = st.text_input('HNR')

        with col2:
            RPDE = st.text_input('RPDE')

        with col3:
            DFA = st.text_input('DFA')

        with col4:
            spread1 = st.text_input('spread1')

        with col5:
            spread2 = st.text_input('spread2')

        with col1:
            D2 = st.text_input('D2')

        with col2:
            PPE = st.text_input('PPE')

        # code for Prediction
        parkinsons_diagnosis = ''

        # creating a button for Prediction    
        if st.button("Parkinson's Test Result"):

            user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                        RAP, PPQ, DDP,Shimmer, Shimmer_dB, APQ3, APQ5,
                        APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]

            user_input = [float(x) for x in user_input]

            parkinsons_prediction = parkinsons_model.predict([user_input])

            if parkinsons_prediction[0] == 1:
                parkinsons_diagnosis = "The person has Parkinson's disease"
            else:
                parkinsons_diagnosis = "The person does not have Parkinson's disease"

        st.success(parkinsons_diagnosis)
