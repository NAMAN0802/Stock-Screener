import streamlit as st
from utils.apis import run_screener

st.markdown('<h1 class="main-header">💾 Saved Screeners</h1>', unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("Please login to view your saved screeners.")
    st.switch_page("pages/auth.py")

if st.session_state.saved_screeners:
    with st.container():
        for screener in st.session_state.saved_screeners:
            st.markdown(f'<div class="screener-card">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.subheader(screener['name'])
                st.write(f"Created: {screener['created_date']}")
                
                # Show criteria summary
                criteria_text = []
                for key, value in screener['criteria'].items():
                    if isinstance(value, dict):
                        if 'min' in value and 'max' in value:
                            criteria_text.append(f"{key.upper()}: {value['min']}-{value['max']}%")
                        elif 'max' in value:
                            criteria_text.append(f"{key.upper()}: <{value['max']}")
                
                if criteria_text:
                    st.write("Criteria: " + ", ".join(criteria_text))
            
            with col2:
                st.metric("Last Run", "2 days ago")
                st.metric("Results", "12 stocks")
            
            with col3:
                if st.button("▶️ Run", key=f"run_{screener['id']}"):
                    results = run_screener(screener['criteria'])
                    st.success(f"Found {len(results)} stocks!")
                    st.dataframe(results, use_container_width=True, hide_index=True)
            
            with col4:
                col4a, col4b = st.columns(2)
                with col4a:
                    if st.button("✏️", key=f"edit_{screener['id']}", help="Edit"):
                        st.info("Edit functionality would open screener builder with pre-filled values")
                with col4b:
                    if st.button("🗑️", key=f"delete_{screener['id']}", help="Delete"):
                        st.session_state.saved_screeners = [s for s in st.session_state.saved_screeners if s['id'] != screener['id']]
                        st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

else:
    st.info("No saved screeners yet. Create your first screener!")
    if st.button("⚙️ Create New Screener"):
        st.session_state.page = "⚙️ Screener Builder"