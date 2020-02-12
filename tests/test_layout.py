from datetime import datetime

from django.test import TestCase
from trionyx import layout as l  # noqa E741

from trionyx.trionyx.models import User


class ModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="info@trionyx.com")
        self.layout = l.Layout(
            l.Row(
                l.Column6(
                    l.Panel(
                        'Left panel',
                        id='left-panel'
                    )
                ),
                l.Column6(
                    l.Panel(
                        'Right panel',
                        id='right-panel'
                    )
                )
            )
        )

    def test_layout_path(self):
        panel, parent = self.layout.find_component_by_path('row.column6[1].panel')
        self.assertEqual(panel.title, 'Right panel')

    def test_layout_id(self):
        panel, parent = self.layout.find_component_by_id('right-panel')
        self.assertEqual(panel.title, 'Right panel')

    def test_remove_component(self):
        self.layout.delete_component(path='row.column6.panel')
        self.layout.delete_component(id='right-panel')
        self.assertInHTML("""
        <div class="row">
            <div class="col-md-6"></div>
            <div class="col-md-6"></div>
        </div>
        """, self.layout.render())

    def test_remove_top_component(self):
        self.layout.delete_component(path='row')
        self.assertInHTML("""<div id="{}"></div>""".format(self.layout.id), self.layout.render())

    def test_remove_invalid_component(self):
        with self.assertRaises(Exception):
            self.layout.delete_component(path='some random path')

    def test_remove_no_params_component(self):
        with self.assertRaises(Exception):
            self.layout.delete_component()

    def test_add_component(self):
        self.layout.add_component(l.Img(), path='row.column6[1].panel', append=True)
        self.layout.add_component(l.Img(), id='left-panel', append=True)

        self.assertInHTML("""
        <div class="row">
            <div class="col-md-6">
                <div id="component-left-panel">
                    <div class="panel panel-default">
                        <div class="panel-heading">Left panel</div>
                        <div class="panel-collapse">
                            <img width="100%" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div id="component-right-panel">
                    <div class="panel panel-default">
                        <div class="panel-heading">Right panel</div>
                        <div class="panel-collapse">
                            <img width="100%" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, self.layout.render())

    def test_input(self):
        self.assertHTMLEqual(l.Input(name='test').render({}), """
        <div class="form-group no-margin ">
            <input type="text" class="form-control" name="test" />
        </div>
        """)

    def test_badge(self):
        badge = l.Badge(html='test')
        badge.set_object(self.user)
        self.assertHTMLEqual(
            badge.render({}),
            f"""<span class="badge bg-theme">test</span>""")

    def test_alert(self):
        self.assertHTMLEqual(l.Alert('trionyx', no_margin=True).render({}), """
        <div class="alert alert-success no-margin">
            trionyx
        </div>
        """)

    def test_button(self):
        button = l.Button('Trionyx')
        button.set_object(self.user)
        self.assertHTMLEqual(button.render({}), """
        <button class="btn btn-flat bg-theme" onclick="window.location.href='/model/trionyx/user/{id}/'; return false;">
            Trionyx
        </button>
        """.format(id=self.user.id))

    def test_button_dialog(self):
        button = l.Button('Trionyx', dialog=True, dialog_reload_tab='general')
        button.set_object(self.user)
        self.assertHTMLEqual(button.render({}), """
        <button class="btn btn-flat bg-theme" onClick="openDialog('/model/trionyx/user/{id}/', {{ callback:function(data, dialog){{
                if (data.success) {{
                    dialog.close();
                    trionyx_reload_tab('general');
                }}
            }} }}); return false;">
            Trionyx
        </button>
        """.format(id=self.user.id))

    def test_ordered_list(self):
        unordered = l.OrderedList(
            {
                'value': 'Item 1',
            },
            {
                'value': 'Item 2',
            }
        )
        unordered.set_object({})
        self.assertHTMLEqual(unordered.render({}), """
        <ol>
            <li>
                Item 1
            </li><li>
                Item 2
            </li>
        </ol>
        """)

    def test_ordered_list_objects(self):
        unordered = l.OrderedList(
            '_index_',
            objects=[['Item 1'], ['Item 2']]
        )
        unordered.set_object({})
        self.assertHTMLEqual(unordered.render({}), """
        <ol>
            <li>
                Item 1
            </li><li>
                Item 2
            </li>
        </ol>
        """)

    def test_progressBar(self):
        progressbar = l.ProgressBar(value=10)
        progressbar.set_object({})
        self.assertHTMLEqual(progressbar.render({}), """
        <div class=" progress progress-md">
            <div aria-valuemax="100" aria-valuemin="0" aria-valuenow="10"
            class=" progress-bar progress-bar-theme" role="progressbar" style="width: 10%">
                <span>
                    10%
                </span>
            </div>
        </div>
        """)

    def test_table_description(self):
        self.assertHTMLEqual(l.TableDescription({
            'label': 'Trionyx',
            'value': 'Test',
        }).render({}), """
        <table class="table table-condensed">
            <tbody>
                <tr>
                    <th style="width: 150px;">
                        Trionyx:
                    </th>
                    <td class="description-value">
                        Test
                    </td>
                </tr>
            </tbody>
        </table>
        """)

    def test_table(self):
        html = l.Table(
            [['column1', 'column2', 'column3']],
            {
                'label': 'Column 1',
            },
            {
                'label': 'Column 2',
            },
            {
                'label': 'Column 3',
            },
            footer=[
                [
                    ['Footer', '123'],
                ],
                {
                    'colspan': 2,
                },
                {
                    'class': 'text-right',
                }
            ]
        ).render({})
        self.assertHTMLEqual(html, """
        <div class="table-responsive">
            <table class="table table-condensed">
                <thead>
                    <tr>
                        <th>Column 1</th>
                        <th>Column 2</th>
                        <th>Column 3</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>column1</td>
                        <td>column2</td>
                        <td>column3</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="2">Footer</td>
                        <td class="text-right">123</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """)

    def test_line_chart(self):
        chart = l.LineChart(
            [
                [datetime.fromtimestamp(1576951711), 1],
                [datetime.fromtimestamp(1576941711), 2],
                [datetime.fromtimestamp(1576931711), 3]
            ],
            'x',
            'y'
        )
        chart.set_object({})

        self.assertEqual(chart.chart_data['labels'], [1576951711000, 1576941711000, 1576931711000])
        self.assertEqual(chart.chart_data['datasets'][0]['data'], [
            {'x': 1576951711000, 'y': 1, 'label': '1'},
            {'x': 1576941711000, 'y': 2, 'label': '2'},
            {'x': 1576931711000, 'y': 3, 'label': '3'}
        ])

    def test_pie_chart(self):
        chart = l.PieChart(
            [['Python3', 60], ['Javascript', 30], ['Sql', 10]],
            'name',
            'value',
        )
        chart.set_object({})

        self.assertEqual(chart.chart_data['labels'], ['Python3', 'Javascript', 'Sql'])
        self.assertEqual(chart.chart_data['datasets'][0]['data'], [60, 30, 10])
