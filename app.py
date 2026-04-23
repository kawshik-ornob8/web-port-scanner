import socket
import streamlit as st

# Set up the web page title and icon
st.set_page_config(page_title="Port Scanner", page_icon="🌐")

st.title("🌐 Python Web Port Scanner")
st.write("A simple, educational port scanner built with Streamlit.")

# --- UI Inputs ---
target = st.text_input("Target IP or Hostname:", value="scanme.nmap.org")

# Put the port inputs side-by-side using columns
col1, col2 = st.columns(2)
with col1:
    start_port = st.number_input("Start Port:", min_value=1, max_value=65535, value=1)
with col2:
    end_port = st.number_input("End Port:", min_value=1, max_value=65535, value=100)

# --- Scanning Logic ---
# This runs only when the user clicks the button
if st.button("Start Scan", type="primary"):
    
    # Validate input
    if start_port > end_port:
        st.error("Start port cannot be greater than End port.")
    else:
        st.write("-" * 50)
        st.write(f"**Scanning target:** {target}")
        
        # UI elements to show real-time progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        open_ports = []
        total_ports = end_port - start_port + 1

        try:
            # Resolve hostname to IP
            target_ip = socket.gethostbyname(target)
            
            for i, port in enumerate(range(start_port, end_port + 1)):
                # Update the progress bar and status text
                progress_percentage = (i + 1) / total_ports
                progress_bar.progress(progress_percentage)
                status_text.text(f"Scanning port {port}...")

                # Socket connection
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5) # Fast timeout for the web
                result = s.connect_ex((target_ip, port))
                
                if result == 0:
                    open_ports.append(port)
                    # Display open port immediately
                    st.success(f"🔓 Port {port} is OPEN")
                
                s.close()
            
            # Finish up
            status_text.text("✅ Scan Complete!")
            if not open_ports:
                st.info("No open ports found in this range.")
                
        except socket.gaierror:
            st.error("Error: Invalid hostname or IP address.")
        except Exception as e:
            st.error(f"An error occurred: {e}")