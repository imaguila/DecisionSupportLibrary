## --------------------------------------------------------------------------------------
## lens_diversity.py
## --------------------------------------------------------------------------------------

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

try:
    from sklearn_extra.cluster import KMedoids
except Exception:
    KMedoids = None

try:
    from sklearn.cluster import HDBSCAN
except Exception:
    HDBSCAN = None


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


def _compute_auto_k(
    x_scaled,
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

            if KMedoids is not None:

                model = KMedoids(
                    n_clusters=k,
                    method="pam",
                    random_state=123
                )

            else:

                model = KMeans(
                    n_clusters=k,
                    random_state=123,
                    n_init=10
                )

            labels = model.fit_predict(
                x_scaled
            )

            if len(set(labels)) > 1:

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


def _fit_kmedoids(
    x_scaled,
    k
):

    if KMedoids is not None:

        model = KMedoids(
            n_clusters=k,
            method="pam",
            random_state=123
        )

        labels = model.fit_predict(
            x_scaled
        )

        method_used = "K-Medoids"

    else:

        model = KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

        labels = model.fit_predict(
            x_scaled
        )

        method_used = "K-Means fallback"

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

        method_used = (
            "HDBSCAN unavailable"
        )

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

    result[
        "diversity_method"
    ] = method_used

    result[
        "diversity_metrics"
    ] = ", ".join(
        metrics_used
    )

    return result


def apply_diversity_lens(
    df,
    dimensions,
    params
):

    result = df.copy()

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

    # ==================================================
    # K-MEDOIDS
    # ==================================================

    if method == "K-Medoids":

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
                x_scaled
            )

            if k < 2:

                return result

        labels, method_used = _fit_kmedoids(
            x_scaled,
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


    # ==================================================
    # HDBSCAN
    # ==================================================

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

            result = result[
                result["cluster"] != -1
            ].copy()

        return result

    return result