import socket
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Set up the web page title and icon
st.set_page_config(page_title="Pro Port Scanner", page_icon="🚀", layout="centered")

# --- Logic: Separate Scanning System ---

def clean_target(target):
    """
    Cleans the input to ensure it's a hostname or IP.
    Example: https://kawshik.dev/about -> kawshik.dev
    """
    target = target.strip()
    if "://" in target:
        target = urlparse(target).netloc
    else:
        # Handle cases like 'kawshik.dev/page'
        target = target.split('/')[0]
    return target

def scan_single_port(target_ip, port):
    """
    Checks a single port. Returns the port number if open, else None.
    """
    try:
        # AF_INET = IPv4, SOCK_STREAM = TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0) # Timeout for fast response
            result = s.connect_ex((target_ip, port))
            if result == 0:
                return port
    except:
        return None
    return None

# --- UI Layout ---

st.title("🚀 Super-Fast Port Scanner")
st.markdown("""
    This version uses **Multi-threading** to scan multiple ports simultaneously.
    It also automatically cleans URLs (removes `https://`).
""")

target_input = st.text_input("Target IP, Hostname, or URL:", placeholder="example.com")

col1, col2, col3 = st.columns(3)
with col1:
    start_port = st.number_input("Start Port:", min_value=1, max_value=65535, value=1)
with col2:
    end_port = st.number_input("End Port:", min_value=1, max_value=65535, value=1024)
with col3:
    # This controls how many threads run at once
    threads = st.select_slider("Scan Speed (Threads):", options=[10, 50, 100, 200], value=100)

if st.button("Launch Scan", type="primary"):
    if not target_input:
        st.warning("Please enter a target.")
    elif start_port > end_port:
        st.error("Invalid range: Start port is higher than End port.")
    else:
        target = clean_target(target_input)
        
        try:
            target_ip = socket.gethostbyname(target)
            st.info(f"🔎 Scanning **{target}** ({target_ip})")
            
            # Progress Bar and Status
            progress_bar = st.progress(0)
            status_text = st.empty()
            found_container = st.container()
            
            open_ports = []
            port_range = range(start_port, end_port + 1)
            total = len(port_range)

            # --- Multi-threading Engine ---
            # ThreadPoolExecutor runs scan_single_port in parallel
            with ThreadPoolExecutor(max_workers=threads) as executor:
                # Map the function to the range of ports
                futures = [executor.submit(scan_single_port, target_ip, p) for p in port_range]
                
                for i, future in enumerate(futures):
                    res = future.result()
                    if res:
                        open_ports.append(res)
                        found_container.success(f"🔓 Port {res} is OPEN")
                    
                    # Update progress every few ports to save UI resources
                    if i % 5 == 0 or i == total - 1:
                        progress_bar.progress((i + 1) / total)
                        status_text.text(f"Progress: {i+1}/{total} ports checked...")

            st.divider()
            if open_ports:
                st.balloons()
                st.success(f"✅ Scan Finished! Found {len(open_ports)} open ports.")
            else:
                st.info("Scan complete. No open ports found.")

        except socket.gaierror:
            st.error("❌ **DNS Error:** Could not resolve host. Check the spelling or your internet connection.")
        except socket.error as e:
            st.error(f"❌ **Connection Error:** {e}")
        except Exception as e:
            st.error(f"❌ **Unexpected Error:** {e}")