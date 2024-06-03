import streamlit as st
import pandas as pd
import plotly.express as px


def main():
    st.title("Streamlit App with Open Dataset")
    st.write(
        "This app showcases some nice possibilities of Streamlit with an open dataset."
    )

    # Load the dataset
    url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
    data = pd.read_csv(url)

    # Select a continent
    continents = data.continent.unique()
    continent = st.selectbox("Select a continent", continents, key="continent")

    # Filter the data
    filtered_data = data[data.continent == continent]

    # Display the data
    st.write("Data for", continent)
    st.write(filtered_data)

    # Create a scatter plot
    fig = px.scatter(
        filtered_data,
        x="gdpPercap",
        y="lifeExp",
        animation_frame="year",
        animation_group="country",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=55,
        range_x=[100, 100000],
        range_y=[25, 90],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Create a bar chart
    fig = px.bar(
        filtered_data, x="country", y="gdpPercap", color="continent", barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Create a line chart
    fig = px.line(filtered_data, x="year", y="lifeExp", color="country")
    st.plotly_chart(fig, use_container_width=True)

    # Create a histogram
    fig = px.histogram(filtered_data, x="gdpPercap", color="continent", nbins=50)
    st.plotly_chart(fig, use_container_width=True)

    # Create a box plot
    fig = px.box(filtered_data, x="continent", y="lifeExp")
    st.plotly_chart(fig, use_container_width=True)

    # Create a violin plot
    fig = px.violin(filtered_data, x="continent", y="gdpPercap")
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
