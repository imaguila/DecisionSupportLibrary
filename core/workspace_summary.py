import streamlit as st

def render_summary( df, dataset ):

    if df is None:
        st.error(
            "Dataset summary cannot be rendered "
            "because the current dataframe is empty."
        )
        return

    with st.expander(  "📊 Dataset Summary", expanded=False ):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric( "Solutions", len(df) )
        with c2:
            st.metric( "Attributes",  len(df.columns) )
        with c3:
            st.metric( "Decision Variables", len( dataset[ "decision_variables" ] ) )

        st.caption(
            f"Decision-variable prefix: "
            f"{dataset['config'].get('var_prefix')}"
        )

        st.download_button(
            label="⬇️ Export Current Subset",
            data=df.to_csv(  index=False ),
            file_name="current_subset.csv",
            mime="text/csv",
            use_container_width=True
        )