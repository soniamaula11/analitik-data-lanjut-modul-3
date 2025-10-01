import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

# Fungsi untuk membuat koneksi ke database
def get_connection():
    """Membuat dan mengembalikan koneksi ke database MySQL."""
    connection = mysql.connector.connect(
        host='localhost',  # misalnya "localhost"
        user='root',
        password='',
        database='db_dal'
    )
    return connection

# Fungsi untuk mengambil data dari database
def get_data_from_db():
    """Mengambil semua data dari tabel pddikti_example dan mengembalikannya sebagai DataFrame."""
    conn = get_connection()
    query = "SELECT * FROM pddikti_example"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Judul utama aplikasi
st.title('Streamlit Simple App')

# Menambahkan navigasi di sidebar
page = st.sidebar.radio("Pilih halaman", ["Dataset", "Visualisasi", "Form Input"])

# Logika untuk halaman "Form Input"
if page == "Form Input":
    st.header("Halaman Form Input")
    # Menggunakan satu blok form untuk input dan tombol submit
    with st.form(key='input_form'):
        input_semester = st.text_input('Semester')
        input_jumlah = st.number_input('Jumlah', min_value=0, format='%d')
        input_program_studi = st.text_input('Program Studi')
        input_universitas = st.text_input('Universitas')
        submit_button = st.form_submit_button(label='Submit Data')
    
    # Logika ini dieksekusi ketika tombol submit di dalam form ditekan
    if submit_button:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO pddikti_example(semester, jumlah, program_studi, universitas)
            VALUES (%s, %s, %s, %s)
            """
            # Eksekusi query dengan data dari form
            cursor.execute(query, (input_semester, input_jumlah, input_program_studi, input_universitas))
            conn.commit()
            st.success("Data successfully submitted to the database!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# Logika untuk halaman "Dataset"
elif page == "Dataset":
    st.header("Halaman Dataset")
    # Mengambil data terbaru dari database dan menampilkannya
    data = get_data_from_db()
    st.write("Data terbaru dari database:")
    st.dataframe(data)

# Logika untuk halaman "Visualisasi"
elif page == "Visualisasi":
    st.header("Halaman Visualisasi")
    
    # Mengambil data dari database untuk konsistensi
    data = get_data_from_db()
    
    if not data.empty:
        # Membuat selectbox untuk memilih universitas
        selected_university = st.selectbox('Pilih Universitas', data['universitas'].unique())
        filtered_data = data[data["universitas"] == selected_university]

        if not filtered_data.empty:
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Membuat plot untuk setiap program studi
            for prog_studi in filtered_data['program_studi'].unique():
                subset = filtered_data[filtered_data['program_studi'] == prog_studi]
                subset = subset.sort_values(by='id', ascending=False)
                ax.plot(subset['semester'], subset['jumlah'], marker='o', linestyle='-', label=prog_studi)

            ax.set_title(f'Visualisasi Data untuk {selected_university}', fontsize=16)
            ax.set_xlabel('Semester', fontsize=12)
            ax.set_ylabel('Jumlah', fontsize=12)
            plt.xticks(rotation=45)
            ax.legend()
            ax.grid(True)
            
            # Menampilkan plot di Streamlit
            st.pyplot(fig)
        else:
            st.warning("Tidak ada data yang tersedia untuk universitas yang dipilih.")
    else:
        st.warning("Tidak ada data di database untuk divisualisasikan.")