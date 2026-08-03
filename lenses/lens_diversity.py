from sklearn.cluster import KMeans


def apply_diversity_lens(
    df,
    dimensions,
    target_size
):

    result = df.copy()

    X = result[
        dimensions
    ].select_dtypes(
        include="number"
    )

    if len(X) < target_size:

        return result

    model = KMeans(
        n_clusters=min(
            target_size,
            len(result)
        ),
        random_state=42
    )

    clusters = model.fit_predict(X)

    result["cluster"] = clusters

    representatives = (

        result

        .groupby("cluster")

        .head(1)

    )

    return representatives