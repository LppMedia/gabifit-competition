"""
Reusable Plotly chart functions for the dashboard.
Each function returns a plotly Figure object.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

BRAND_COLORS = ["#FF6B35", "#004E89", "#1A936F", "#C84B31", "#A8DADC", "#457B9D"]
PLATFORM_COLORS = {"instagram": "#E1306C", "tiktok": "#010101", "both": "#FF6B35"}


def followers_vs_engagement(df: pd.DataFrame) -> go.Figure:
    """Scatter: Followers vs Engagement Rate, bubble size = post count."""
    if df.empty:
        return go.Figure()

    x_col = "ig_followers" if "ig_followers" in df.columns else "total_social_followers"
    y_col = "ig_engagement_rate" if "ig_engagement_rate" in df.columns else None
    if y_col is None or y_col not in df.columns:
        return go.Figure()

    plot_df = df[[x_col, y_col, "full_name", "primary_platform"]].dropna()
    size_col = None
    if "ig_posts_count" in df.columns:
        plot_df = plot_df.copy()
        plot_df["post_size"] = df["ig_posts_count"].clip(lower=1).fillna(10)
        size_col = "post_size"

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color="primary_platform",
        size=size_col,
        hover_name="full_name",
        color_discrete_map=PLATFORM_COLORS,
        labels={x_col: "Followers", y_col: "Engagement Rate (%)"},
        title="Followers vs Engagement Rate",
    )
    fig.update_layout(legend_title_text="Platform")
    return fig


def followers_bar_comparison(df: pd.DataFrame) -> go.Figure:
    """Grouped bar: Instagram vs TikTok followers per coach."""
    if df.empty:
        return go.Figure()

    has_ig = "ig_followers" in df.columns
    has_tt = "tt_followers" in df.columns
    if not has_ig and not has_tt:
        return go.Figure()

    plot_df = df[["full_name"]].copy()
    if has_ig:
        plot_df["Instagram"] = df["ig_followers"].fillna(0)
    if has_tt:
        plot_df["TikTok"] = df["tt_followers"].fillna(0)

    plot_df = plot_df.sort_values(
        "Instagram" if has_ig else "TikTok", ascending=False
    ).head(20)

    fig = go.Figure()
    if has_ig:
        fig.add_trace(go.Bar(name="Instagram", x=plot_df["full_name"], y=plot_df["Instagram"], marker_color=PLATFORM_COLORS["instagram"]))
    if has_tt:
        fig.add_trace(go.Bar(name="TikTok", x=plot_df["full_name"], y=plot_df["TikTok"], marker_color=PLATFORM_COLORS["tiktok"]))

    fig.update_layout(
        barmode="group",
        title="Followers by Platform (Top 20)",
        xaxis_tickangle=-45,
        yaxis_title="Followers",
        xaxis_title="Coach",
        legend_title_text="Platform",
    )
    return fig


def platform_distribution_pie(df: pd.DataFrame) -> go.Figure:
    """Donut chart: distribution of platform usage."""
    if df.empty or "primary_platform" not in df.columns:
        return go.Figure()

    counts = df["primary_platform"].value_counts().reset_index()
    counts.columns = ["platform", "count"]

    fig = px.pie(
        counts,
        names="platform",
        values="count",
        hole=0.4,
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        title="Platform Distribution",
    )
    return fig


def price_range_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar showing each coach's price range (min–max)."""
    if df.empty:
        return go.Figure()

    needed = ["full_name", "min_price_usd", "max_price_usd"]
    if not all(c in df.columns for c in needed):
        return go.Figure()

    plot_df = df[needed].dropna(subset=["min_price_usd"]).copy()
    if plot_df.empty:
        return go.Figure()

    plot_df["max_price_usd"] = plot_df["max_price_usd"].fillna(plot_df["min_price_usd"])
    plot_df = plot_df.sort_values("min_price_usd")

    fig = go.Figure()
    for _, row in plot_df.iterrows():
        fig.add_trace(go.Bar(
            name=row["full_name"],
            y=[row["full_name"]],
            x=[row["max_price_usd"] - row["min_price_usd"]],
            base=row["min_price_usd"],
            orientation="h",
            marker_color=BRAND_COLORS[0],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['full_name']}</b><br>"
                f"Min: ${row['min_price_usd']:.0f} USD<br>"
                f"Max: ${row['max_price_usd']:.0f} USD<extra></extra>"
            ),
        ))

    fig.update_layout(
        title="Coach Pricing Ranges (USD)",
        xaxis_title="Price (USD)",
        yaxis_title="Coach",
        height=max(300, len(plot_df) * 30 + 100),
        barmode="overlay",
    )
    return fig


def price_box_by_service(df: pd.DataFrame) -> go.Figure:
    """Box plot of price distribution by service type."""
    if df.empty:
        return go.Figure()

    service_map = {
        "offers_online": "Online Coaching",
        "offers_in_person": "In-Person",
        "offers_nutrition": "Nutrition",
        "offers_transformation": "Transformation",
    }

    rows = []
    for col, label in service_map.items():
        if col in df.columns and "min_price_usd" in df.columns:
            sub = df[df[col] == True]["min_price_usd"].dropna()
            for val in sub:
                rows.append({"service": label, "price_usd": val})

    if not rows:
        return go.Figure()

    plot_df = pd.DataFrame(rows)
    fig = px.box(
        plot_df,
        x="service",
        y="price_usd",
        color="service",
        color_discrete_sequence=BRAND_COLORS,
        title="Price Distribution by Service Type",
        labels={"price_usd": "Price (USD)", "service": "Service"},
    )
    fig.update_layout(showlegend=False)
    return fig


def services_heatmap(df: pd.DataFrame) -> go.Figure:
    """Horizontal stacked bar showing which services each coach offers."""
    if df.empty:
        return go.Figure()

    service_cols = {
        "offers_online": "Online",
        "offers_in_person": "In-Person",
        "offers_nutrition": "Nutrition",
        "offers_transformation": "Transformation",
        "offers_group": "Group",
        "has_lead_magnet": "Lead Magnet",
    }

    available = {col: label for col, label in service_cols.items() if col in df.columns}
    if not available:
        return go.Figure()

    plot_df = df[["full_name"] + list(available.keys())].copy()
    plot_df = plot_df.set_index("full_name")

    fig = go.Figure()
    for col, label in available.items():
        values = plot_df[col].fillna(False).astype(int)
        fig.add_trace(go.Bar(
            name=label,
            x=values.values,
            y=plot_df.index,
            orientation="h",
        ))

    fig.update_layout(
        barmode="stack",
        title="Services Offered by Coach",
        xaxis_title="Count",
        height=max(400, len(plot_df) * 25 + 100),
        legend_title_text="Service",
    )
    return fig


def services_count_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart: how many coaches offer each service."""
    if df.empty:
        return go.Figure()

    service_cols = {
        "offers_online": "Online Coaching",
        "offers_in_person": "In-Person Training",
        "offers_nutrition": "Nutrition Plan",
        "offers_transformation": "Transformation Program",
        "offers_group": "Group Classes",
        "has_lead_magnet": "Lead Magnet",
        "has_website": "Has Website",
    }

    labels, counts = [], []
    for col, label in service_cols.items():
        if col in df.columns:
            labels.append(label)
            counts.append(int(df[col].fillna(False).sum()))

    if not labels:
        return go.Figure()

    fig = px.bar(
        x=labels,
        y=counts,
        color=counts,
        color_continuous_scale="Oranges",
        title="Number of Coaches Offering Each Service",
        labels={"x": "Service", "y": "Number of Coaches"},
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    return fig


def cta_distribution_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart: CTA channel distribution."""
    if df.empty or "top_cta_channel" not in df.columns:
        return go.Figure()

    counts = df["top_cta_channel"].value_counts().reset_index()
    counts.columns = ["cta_type", "count"]

    label_map = {
        "whatsapp": "WhatsApp",
        "linktree": "Linktree",
        "direct_website": "Direct Website",
        "email": "Email",
        "none": "No CTA",
    }
    counts["cta_label"] = counts["cta_type"].map(label_map).fillna(counts["cta_type"])

    fig = px.bar(
        counts,
        x="cta_label",
        y="count",
        color="cta_label",
        color_discrete_sequence=BRAND_COLORS,
        title="Primary CTA Channel Distribution",
        labels={"cta_label": "CTA Channel", "count": "Number of Coaches"},
    )
    fig.update_layout(showlegend=False)
    return fig


def engagement_vs_lead_magnet(df: pd.DataFrame) -> go.Figure:
    """Scatter: engagement rate vs whether coach has a lead magnet."""
    if df.empty or "ig_engagement_rate" not in df.columns or "has_lead_magnet" not in df.columns:
        return go.Figure()

    plot_df = df[["full_name", "ig_engagement_rate", "has_lead_magnet"]].dropna()
    plot_df["Has Lead Magnet"] = plot_df["has_lead_magnet"].map({True: "Yes", False: "No"})

    fig = px.strip(
        plot_df,
        x="Has Lead Magnet",
        y="ig_engagement_rate",
        color="Has Lead Magnet",
        hover_name="full_name",
        color_discrete_map={"Yes": BRAND_COLORS[0], "No": BRAND_COLORS[1]},
        title="Engagement Rate vs Lead Magnet Presence",
        labels={"ig_engagement_rate": "IG Engagement Rate (%)"},
    )
    return fig


def funnel_sankey(df: pd.DataFrame) -> go.Figure:
    """Sankey diagram: Platform -> CTA Type -> Conversion Action."""
    if df.empty:
        return go.Figure()

    # Build node and link lists
    nodes = ["Instagram", "TikTok", "WhatsApp", "Linktree", "Direct Website", "No CTA",
             "Direct Sale", "Lead Magnet", "Contact Form", "Unknown"]
    node_indices = {n: i for i, n in enumerate(nodes)}

    # Platform -> CTA flows
    flows = []

    def add_flow(source, target, value):
        if value > 0:
            flows.append((node_indices.get(source, 0), node_indices.get(target, 0), value))

    if "primary_platform" in df.columns and "top_cta_channel" in df.columns:
        cta_label_map = {
            "whatsapp": "WhatsApp",
            "linktree": "Linktree",
            "direct_website": "Direct Website",
            "none": "No CTA",
            "email": "No CTA",
        }
        for platform_val, platform_label in [("instagram", "Instagram"), ("tiktok", "TikTok"), ("both", "Instagram")]:
            sub = df[df["primary_platform"] == platform_val]
            for cta_val, cta_label in cta_label_map.items():
                count = len(sub[sub["top_cta_channel"] == cta_val])
                add_flow(platform_label, cta_label, count)

    # CTA -> Conversion action (heuristic based on has_website + has_lead_magnet)
    if "has_lead_magnet" in df.columns and "top_cta_channel" in df.columns:
        with_magnet = df[df["has_lead_magnet"] == True]
        add_flow("Linktree", "Lead Magnet", len(with_magnet[with_magnet["top_cta_channel"] == "linktree"]))
        add_flow("Direct Website", "Lead Magnet", len(with_magnet[with_magnet["top_cta_channel"] == "direct_website"]))
        add_flow("WhatsApp", "Direct Sale", len(df[df["top_cta_channel"] == "whatsapp"]))
        if "has_contact_form" in df.columns:
            add_flow("Direct Website", "Contact Form", len(df[df["has_contact_form"] == True]))

    if not flows:
        return go.Figure()

    sources = [f[0] for f in flows]
    targets = [f[1] for f in flows]
    values = [f[2] for f in flows]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=["#E1306C", "#010101", "#25D366", "#43A8C7", "#FF6B35",
                   "#999999", "#1A936F", "#C84B31", "#457B9D", "#CCCCCC"],
        ),
        link=dict(source=sources, target=targets, value=values),
    ))
    fig.update_layout(title="Marketing Funnel: Platform -> CTA -> Conversion", font_size=12)
    return fig
