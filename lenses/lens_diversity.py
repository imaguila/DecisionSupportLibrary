def _build_partition_model(
    method,
    k
):

    if method == "K-Medoids":

        if KMedoids is not None:

            return KMedoids(
                n_clusters=k,
                method="pam",
                random_state=123
            )

        return KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

    if method == "K-Means":

        return KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

    if method == "Agglomerative":

        return AgglomerativeClustering(
            n_clusters=k
        )

    return KMeans(
        n_clusters=k,
        random_state=123,
        n_init=10
    )


def _compute_auto_k(
    x_scaled,
    method,
    max_k=10
):

    n = len(
        x_scaled
    )

    if n < 3:

        return 1, None

    best_k = 2
    best_score = -1

    upper_k = min(
        max_k,
        n - 1
    )

    for k in range(
        2,
        upper_k + 1
    ):

        try:

            model = _build_partition_model(
                method,
                k
            )

            labels = model.fit_predict(
                x_scaled
            )

    if params["method"] in [
        "K-Medoids",
        "K-Means",
        "Agglomerative"
    ]:

        params["k_mode"] = st.radio(
            "Number of Clusters",
            [
                "Auto",
                "Manual"
            ],
            horizontal=True,
            key="div_k_mode"
        )

        if params["k_mode"] == "Manual":

            max_k = max(
                2,
                min(
                    10,
                    max_n
                )
            )

            default_k = min(
                3,
                max_k
            )

            params["k"] = st.slider(
                "k Clusters",
                2,
                max_k,
                default_k,
                key="div_k"
            )

        else:

            st.caption(
                "Auto mode selects k using silhouette score."
            )

    elif params["method"] == "HDBSCAN":

        params["cluster_size_mode"] = st.radio(
            "Cluster Size",
            [
                "Auto",
                "Manual"
            ],
            horizontal=True,
            key="div_hdbscan_size_mode"
        )

        if params["cluster_size_mode"] == "Auto":

            params["granularity"] = st.selectbox(
                "Cluster Granularity",
                [
                    "Small (~5%)",
                    "Medium (~10%)",
                    "Large (~20%)"
                ],
                index=1,
                key="div_hdbscan_granularity"
            )


        else:

            default_min_cluster_size = max(
                2,
                int(
                    0.10 * max_n
                )
            )

            params["min_cluster_size"] = st.slider(
                "Minimum Cluster Size",
                2,
                max(
                    2,
                    max_n
                ),
                default_min_cluster_size,
                key="div_hdbscan_min_cluster_size"
            )

        params["exclude_noise"] = st.checkbox(
            "Exclude noise solutions",
            value=True,
            key="div_hdbscan_exclude_noise"
        )

        st.caption(
            "If HDBSCAN returns mostly noise, try Small or Medium "
            "granularity, or disable noise exclusion."
        )

    st.caption(
        "Diversity structures the current subset into clusters "
        "instead of applying a preference score."
    )

    return params


# =====================================================
# HELPERS
# =====================================================

def _valid_numeric_metrics(
    df,
    metrics
):

    return [
        metric
        for metric in metrics
        if (
            metric in df.columns
            and pd.api.types.is_numeric_dtype(
                df[metric]
            )
        )
    ]


def _prepare_matrix(
    df,
    metrics
):

    x = df[
        metrics
    ].copy()

    x = x.fillna(
        x.median(
            numeric_only=True
        )
    )

    scaler = StandardScaler()

    x_scaled = scaler.fit_transform(
        x
    )

    return x_scaled

def _build_partition_model(
    method,
    k
):

    if method == "K-Medoids":

        if KMedoids is not None:

            return KMedoids(
                n_clusters=k,
                method="pam",
                random_state=123
            )

        return KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

    if method == "K-Means":

        return KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

    if method == "Agglomerative":

        return AgglomerativeClustering(
            n_clusters=k
        )

    return KMeans(
        n_clusters=k,
        random_state=123,
        n_init=10
    )


def _compute_auto_k(
    x_scaled,
    method,
    max_k=10
):

    n = len(
        x_scaled
    )

    if n < 3:

        return 1, None

    best_k = 2
    best_score = -1

    upper_k = min(
        max_k,
        n - 1
    )

    for k in range(
        2,
        upper_k + 1
    ):

        try:

            model = _build_partition_model(
                method,
                k
            )

            labels = model.fit_predict(
                x_scaled
            )

            unique_labels = set(
                labels
            )

            if (
                len(unique_labels) > 1
                and
                len(unique_labels) < n
            ):

                score = silhouette_score(
                    x_scaled,
                    labels
                )

                if score > best_score:

                    best_score = score
                    best_k = k

        except Exception:

            pass

    return best_k, best_score


def _fit_partition_clustering(
    x_scaled,
    method,
    k
):

    model = _build_partition_model(
        method,
        k
    )

    labels = model.fit_predict(
        x_scaled
    )

    if (
        method == "K-Medoids"
        and
        KMedoids is None
    ):

        method_used = "K-Means fallback"

    else:

        method_used = method

    return labels, method_used


def _fit_hdbscan(
    x_scaled,
    min_cluster_size
):

    if HDBSCAN is None:

        labels = [
            0
            for _ in range(
                len(x_scaled)
            )
        ]

        method_used = "HDBSCAN unavailable"

        return labels, method_used

    model = HDBSCAN(
        min_cluster_size=min_cluster_size
    )

    labels = model.fit_predict(
        x_scaled
    )

    method_used = "HDBSCAN"

    return labels, method_used






def _add_cluster_labels(
    result,
    labels,
    method_used,
    metrics_used
):

    result = result.copy()

    result[
        "cluster"
    ] = labels

    result[
        "cluster_str"
    ] = result[
        "cluster"
    ].astype(
        str
    )

    result[
        "cluster_str"
    ] = result[
        "cluster_str"
    ].replace(
        "-1",
        "Noise"
    )

    cluster_sizes = (
        result
        .groupby(
            "cluster_str"
        )["id"]
        .transform(
            "size"
        )
    )

    result[
        "group_label"
    ] = (
        "Cluster "
        +
        result["cluster_str"]
        +
        " (n="
        +
        cluster_sizes.astype(
            str
        )
        +
        ")"
    )

    n_clusters = (
        result["cluster"]
        .dropna()
        .astype(int)
        .loc[
            lambda values: values != -1
        ]
        .nunique()
    )

    noise_count = (
        result["cluster"]
        .eq(-1)
        .sum()
    )

    result[
        "diversity_method"
    ] = method_used

    result[
        "diversity_metrics"
    ] = ", ".join(
        metrics_used
    )

    result[
        "diversity_n_clusters"
    ] = n_clusters

    result[
        "diversity_noise_count"
    ] = noise_count

    return result

# =====================================================
# APPLY
# =====================================================

def apply(
    df,
    params,
    dataset
):

    result = df.copy()

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    method = params.get(
        "method",
        "K-Medoids"
    )

    cluster_metrics = params.get(
        "cluster_metrics",
        dimensions
    )

    cluster_metrics = _valid_numeric_metrics(
        result,
        cluster_metrics
    )

    if len(cluster_metrics) < 2:

        return result

    if len(result) < 2:

        return result

    x_scaled = _prepare_matrix(
        result,
        cluster_metrics
    )

    if method in [
        "K-Medoids",
        "K-Means",
        "Agglomerative"
    ]:

        k_mode = params.get(
            "k_mode",
            "Auto"
        )

        if k_mode == "Manual":

            k = params.get(
                "k",
                2
            )

            k = max(
                2,
                min(
                    k,
                    len(result)
                )
            )

            silhouette = None

        else:

            k, silhouette = _compute_auto_k(
                x_scaled,
                method
            )

            if k < 2:

                return result

        labels, method_used = _fit_partition_clustering(
            x_scaled,
            method,
            k
        )

        result = _add_cluster_labels(
            result,
            labels,
            method_used,
            cluster_metrics
        )

        result[
            "diversity_k"
        ] = k

        if silhouette is not None:

            result[
                "diversity_silhouette"
            ] = silhouette

        return result
    
    if method == "HDBSCAN":

        n = len(
            result
        )

        size_mode = params.get(
            "cluster_size_mode",
            "Auto"
        )

        if size_mode == "Manual":

            min_cluster_size = params.get(
                "min_cluster_size",
                max(
                    2,
                    int(
                        0.1 * n
                    )
                )
            )

        else:

            granularity = params.get(
                "granularity",
                "Medium (~10%)"
            )

            if granularity == "Small (~5%)":

                min_cluster_size = max(
                    2,
                    int(
                        0.05 * n
                    )
                )

            elif granularity == "Large (~20%)":

                min_cluster_size = max(
                    2,
                    int(
                        0.20 * n
                    )
                )

            else:

                min_cluster_size = max(
                    2,
                    int(
                        0.10 * n
                    )
                )

        labels, method_used = _fit_hdbscan(
            x_scaled,
            min_cluster_size
        )

        result = _add_cluster_labels(
            result,
            labels,
            method_used,
            cluster_metrics
        )

        result[
            "diversity_min_cluster_size"
        ] = min_cluster_size

        exclude_noise = params.get(
            "exclude_noise",
            True
        )

        if exclude_noise:

            filtered_result = result[
                result["cluster"] != -1
            ].copy()

            if filtered_result.empty:

                result[
                    "diversity_warning"
                ] = (
                    "All solutions were classified as noise. "
                    "Noise exclusion was not applied."
                )

                return result

            return filtered_result

        return result

    return result



# =====================================================
# FEEDBACK
# =====================================================

def _safe_first_value(
    df,
    column
):

    if column not in df.columns:

        return None

    values = (
        df[column]
        .dropna()
    )

    if values.empty:

        return None

    return values.iloc[0]


def render_feedback(
    lens_df
):

    if lens_df is None:

        st.warning(
            "No clustering result is available."
        )

        return

    if lens_df.empty:

        st.warning(
            "The clustering lens returned an empty subset. "
            "Try reducing the HDBSCAN cluster size or disabling noise exclusion."
        )

        return

    warning_value = _safe_first_value(
        lens_df,
        "diversity_warning"
    )

    if warning_value is not None:

        st.warning(
            warning_value
        )

    n_clusters = _safe_first_value(
        lens_df,
        "diversity_n_clusters"
    )

    if n_clusters is not None:

        st.info(
            f"Clusters detected: {int(n_clusters)}"
        )

    k_value = _safe_first_value(
        lens_df,
        "diversity_k"
    )

    if k_value is not None:

        st.caption(
            f"Selected k: {int(k_value)}"
        )

    silhouette_value = _safe_first_value(
        lens_df,
        "diversity_silhouette"
    )

    if silhouette_value is not None:

        st.caption(
            f"Silhouette score: {silhouette_value:.3f}"
        )

    min_cluster_size = _safe_first_value(
        lens_df,
        "diversity_min_cluster_size"
    )

    if min_cluster_size is not None:

        st.caption(
            f"Minimum cluster size: {int(min_cluster_size)}"
        )

    noise_count = _safe_first_value(
        lens_df,
        "diversity_noise_count"
    )

    if noise_count is not None:

        if int(noise_count) > 0:

            st.caption(
                f"Noise solutions: {int(noise_count)}"
            )