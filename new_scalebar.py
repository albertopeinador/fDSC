import plotly.graph_objs as go
import numpy as np

# Function to add a vertical scale bar in the top-left corner
def add_scalebar(fig, xaxis_range, yaxis_range, scale_factor=1.0, barcolor='black', barwidth=2):
    # Calculate the vertical scale bar size dynamically based on the y-axis range
    sizey = np.diff(yaxis_range)[0] / 5 * scale_factor  # Dynamically set based on y-axis range and scaling factor

    # Set the position for the vertical scale bar in the top-left corner
    x_offset = xaxis_range[0] + (np.diff(xaxis_range)[0] * 0.05)  # Slightly to the right of the x min value
    y_offset = yaxis_range[1] - (np.diff(yaxis_range)[0] * 0.1)  # Slightly below the max y value (for padding)

    # Add the vertical scale bar
    fig.add_shape(
        type="line",
        x0=x_offset, y0=y_offset,
        x1=x_offset, y1=y_offset - sizey,  # Vertical bar going down
        line=dict(color=barcolor, width=barwidth),
    )

    # Add annotation (label) for the vertical scale bar
    fig.add_annotation(
        x=x_offset - (np.diff(xaxis_range)[0] * 0.02),  # Adjusted slightly to the left
        y=y_offset - sizey / 2,  # Center the label vertically
        text=f"{sizey:.2f} mW", showarrow=False,  # Customize the label text
        font=dict(size=14, color = 'black'), textangle=-90,  # Rotate text vertically
        xshift=-5,  # Fine-tune horizontal position of label
        yshift=0     # Fine-tune vertical position of label
    )

