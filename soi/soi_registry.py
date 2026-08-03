import streamlit as st


def render_soi_registry(
    active_lens,
    soi_df
):

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []

    if active_lens == "None":

        return

    st.markdown("---")

    default_name = (
        f"{active_lens} "
        f"#{len(st.session_state.saved_sois)+1}"
    )

    soi_name = st.text_input(
        "SOI Name",
        value=default_name,
        key="soi_name"
    )

    if st.button(
        "💾 Save Current SOI",
        use_container_width=True
    ):

        existing = [

            soi["name"]

            for soi in st.session_state.saved_sois

        ]

        if soi_name in existing:

            st.warning(
                "A SOI with that name already exists."
            )

        else:

            st.session_state.saved_sois.append(

                {
                    "name": soi_name,
                    "lens": active_lens,
                    "ids": soi_df["id"].tolist()
                }

            )

            st.success(
                f"SOI '{soi_name}' saved."
            )

    if st.session_state.saved_sois:

        st.markdown(
            "##### Saved SOIs"
        )

        for soi in st.session_state.saved_sois:

            st.caption(
                f"• {soi['name']} "
                f"({len(soi['ids'])})"
            )