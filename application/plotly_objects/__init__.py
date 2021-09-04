import logging

import plotly.graph_objects as go
import pandas as pd

map_token = 'pk.eyJ1IjoiZG11cmFraG92c2t5aSIsImEiOiJja29jeG9wbDQwdjh1Mm9wZ3Bvbm1ndmYzIn0.qeqHa9f5UB3iY0_vdhiXgA'

ZOOM = 4
MARKER_SIZE = 15
NODE_SIZE = 20

BASE_MARKER_COLOR = 'blue'
SELECTED_MARKER_COLOR = 'red'
HIGHLIGHTED_NODE_COLOR = 'green'


class PlotlyMap:

    def __init__(self, cities=None):
        self._cities = cities
        self._fig = go.Figure()
        self._selected: pd.DataFrame = pd.DataFrame()

    @staticmethod
    def cleaned_map(df, zoom=1) -> (go.Figure, tuple, float):
        fig, _, _ = PlotlyMap(cities=df)._get_map(initial=True, zoom=zoom,
                                                  center=(df.long.mean(), df.lat.mean()))
        return fig

    @staticmethod
    def get_featured_map(df: pd.DataFrame,
                         selected: list,
                         highlight_path=None,
                         second_highlight_path=None,
                         highlight_nodes=None,
                         zoom: float = ZOOM,
                         center: tuple = (0, 0)) -> (go.Figure, tuple, float):
        return PlotlyMap(cities=df)._get_map(selected=selected, zoom=zoom, center=center,
                                             highlight_path=highlight_path,
                                             second_highlight_path=second_highlight_path,
                                             highlight_nodes=highlight_nodes
                                             )

    def _get_map(self,
                 selected: list = None,
                 highlight_path=None,
                 second_highlight_path=None,
                 highlight_nodes=None,
                 zoom: float = 5,
                 center: tuple = (0, 0),
                 initial: bool = False) -> (go.Figure, tuple, float):

        logger = logging.getLogger('local_writer')

        if highlight_path is not None:
            logger.debug(f'First highlight path: {highlight_path}')
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
            logger.debug(f'Second highlight path: {second_highlight_path}')
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
        if selected is not None:
            self._selected = self._cities.loc[self._cities.index.isin(selected)].copy()

            self._fig.add_trace(go.Scattermapbox(
                lat=self._selected.lat,
                lon=self._selected.long,
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=MARKER_SIZE,
                    color=SELECTED_MARKER_COLOR,
                    opacity=1
                ),
                text=self._selected.index,
                hoverinfo='text'
            ))

        """
        Highlighting nodes
        """
        if highlight_nodes is not None:
            logger.debug(f'Highlighted nodes: {highlight_nodes}')
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
                    lat=center[1],
                    lon=center[0],
                ),
                pitch=0,
                style='light',
                zoom=zoom
            ),
        )

        return self._fig, center, zoom
