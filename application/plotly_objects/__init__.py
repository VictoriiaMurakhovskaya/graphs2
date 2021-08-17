import plotly.graph_objects as go

map_token = 'pk.eyJ1IjoiZG11cmFraG92c2t5aSIsImEiOiJja29jeG9wbDQwdjh1Mm9wZ3Bvbm1ndmYzIn0.qeqHa9f5UB3iY0_vdhiXgA'

ZOOM = 4
MARKER_SIZE = 15
NODE_SIZE = 20

BASE_MARKER_COLOR = 'blue'
SELECTED_MARKER_COLOR = 'red'
HIGHLIGHTED_NODE_COLOR = 'green'


class BaseMap:

    def __init__(self, cities=None, selected=None):
        self._cities = cities
        self._selected = selected
        self._fig = go.Figure()
        self._zoom = ZOOM

    @property
    def cities(self):
        return self._cities

    @cities.getter
    def cities(self):
        return self._cities

    @cities.setter
    def cities(self, value):
        self._cities = value

    @property
    def selected(self):
        return self._selected

    @selected.getter
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

    @property
    def zoom(self):
        return self._zoom

    @zoom.getter
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = value

    def cleaned_map(self, selected=False):
        if selected:
            self._selected = None

        self._fig.data = []
        return self.get_map()

    def get_map(self, highlight_path=None, second_highlight_path=None, highlight_nodes=None, initial=False):

        if highlight_path is not None:
            if isinstance(highlight_path, list):
                connect = self._cities.loc[self._cities.index.isin(highlight_path)]
                connect = connect.reindex(index=highlight_path)
                self._fig.add_trace(go.Scattermapbox(
                    lat=connect.lat,
                    lon=connect.long,
                    mode='lines',
                    line=go.scattermapbox.Line(
                        color='yellow',
                        width=4
                    )
                ))
            elif isinstance(highlight_path, dict):
                for k in highlight_path.keys():
                    lat_lst = [self._cities.at[highlight_path[k][0], 'lat'],
                               self._cities.at[highlight_path[k][1], 'lat']]
                    long_lst = [self._cities.at[highlight_path[k][0], 'long'],
                                self._cities.at[highlight_path[k][1], 'long']]
                    self._fig.add_trace(go.Scattermapbox(
                        lat=lat_lst,
                        lon=long_lst,
                        mode='lines',
                        line=go.scattermapbox.Line(
                            color='yellow',
                            width=4
                        )
                    ))
            else:
                raise TypeError("Incorrect input type")

        if second_highlight_path is not None:
            if isinstance(second_highlight_path, list):
                connect = self._cities.loc[self._cities.index.isin(second_highlight_path)]
                connect = connect.reindex(index=highlight_path)
                self._fig.add_trace(go.Scattermapbox(
                    lat=connect.lat,
                    lon=connect.long,
                    mode='lines',
                    line=go.scattermapbox.Line(
                        color='green',
                        width=2
                    )
                ))
            elif isinstance(second_highlight_path, dict):
                for k in second_highlight_path.keys():
                    lat_lst = [self._cities.at[second_highlight_path[k][0], 'lat'],
                               self._cities.at[second_highlight_path[k][1], 'lat']]
                    long_lst = [self._cities.at[second_highlight_path[k][0], 'long'],
                                self._cities.at[second_highlight_path[k][1], 'long']]
                    self._fig.add_trace(go.Scattermapbox(
                        lat=lat_lst,
                        lon=long_lst,
                        mode='lines',
                        line=go.scattermapbox.Line(
                            color='green',
                            width=2
                        )
                    ))
            else:
                raise TypeError("Incorrect input type")

        """
        Base markers
        """
        self._fig.add_trace(go.Scattermapbox(
            lat=self._cities.lat,
            lon=self._cities.long,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=MARKER_SIZE,
                color=BASE_MARKER_COLOR,
                opacity=1
            ),
            text=self._cities.index,
            hoverinfo='text'
        ))

        """
        Selected items
        """
        if self._selected is not None:
            self._fig.add_trace(go.Scattermapbox(
                lat=self._selected.lat,
                lon=self._selected.long,
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=MARKER_SIZE,
                    color=SELECTED_MARKER_COLOR,
                    opacity=1
                ),
                hoverinfo='text'
            ))

        """
        Highlighting nodes
        """
        if highlight_nodes is not None:
            highlight_lat, highlight_lon = [], []
            for item in highlight_nodes:
                highlight_lon.append(self._cities.at[item, 'long'])
                highlight_lat.append(self._cities.at[item, 'lat'])
            self._fig.add_trace(go.Scattermapbox(
                lat=highlight_lat,
                lon=highlight_lon,
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=NODE_SIZE,
                    color=HIGHLIGHTED_NODE_COLOR,
                    opacity=1
                ),
                hoverinfo='text'
            ))




        if initial:
            self._zoom = ZOOM
            self._fig.update_layout(
                autosize=True,
                clickmode='event',
                showlegend=False,
                margin_l=0,
                margin_t=0,
                mapbox=dict(
                    accesstoken=map_token,
                    bearing=0,
                    center=dict(
                        lat=self._cities.lat.mean(),
                        lon=self._cities.long.mean(),
                    ),
                    pitch=0,
                    zoom=self._zoom,
                    style='light'
                ),
            )
        else:
            self._fig.update_layout(
                autosize=True,
                clickmode='event',
                showlegend=False,
                margin_l=0,
                margin_t=0,
                mapbox=dict(
                    accesstoken=map_token,
                    bearing=0,
                    pitch=0,
                    zoom=self._zoom,
                    style='light'
                ),
            )

        return self._fig
