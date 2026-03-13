"""
MIT License

Copyright (C) 2026 ROCKY4546
https://github.com/rocky4546

This file is part of Cabernet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
"""

import random
import uuid

from lib.plugins.plugin_obj import PluginObj

from .plutotv_instance import PlutoTVInstance
from ..lib import translations


class PlutoTV(PluginObj):

    def __init__(self, _plugin):
        super().__init__(_plugin)
        if not self.config_obj.data[_plugin.name.lower()]['enabled']:
            return

        self.clientid_list = []
        for i in range(self.config_obj.data[_plugin.name.lower()]['player-tuner_count']):
            self.clientid_list.append(str(uuid.uuid4()))

        self.unc_plutotv_boot = self.uncompress(translations.plutotv_boot)
        self.unc_plutotv_channels = self.uncompress(translations.plutotv_channels)
        self.unc_plutotv_service = self.uncompress(translations.plutotv_service)
        self.unc_plutotv_categories = self.uncompress(translations.plutotv_categories)
        self.unc_plutotv_epg = self.uncompress(translations.plutotv_epg)

        # create an instance if none are present
        self.enable_instance(self.namespace, None)
        for inst in _plugin.instances:
            self.instances[inst] = PlutoTVInstance(self, inst)

    def scheduler_tasks(self):
        sched_ch_hours = self.utc_to_local_time(23)
        sched_ch_mins = random.randint(1, 55)
        sched_ch = '{:0>2d}:{:0>2d}'.format(sched_ch_hours, sched_ch_mins)
        if self.scheduler_db.save_task(
                'Channels',
                'Refresh {} Channels'.format(self.namespace),
                self.name,
                None,
                'refresh_channels',
                20,
                'inline',
                'Pulls channel lineup from {}'.format(self.namespace)
        ):
            self.scheduler_db.save_trigger(
                'Channels',
                'Refresh {} Channels'.format(self.namespace),
                'startup')
            self.scheduler_db.save_trigger(
                'Channels',
                'Refresh {} Channels'.format(self.namespace),
                'daily',
                timeofday=sched_ch
            )
        if self.scheduler_db.save_task(
                'EPG',
                'Refresh {} EPG'.format(self.namespace),
                self.name,
                None,
                'refresh_epg',
                10,
                'thread',
                'Pulls channel program data from {}'.format(self.namespace)
        ):
            self.scheduler_db.save_trigger(
                'EPG',
                'Refresh {} EPG'.format(self.namespace),
                'interval',
                interval=320,
                randdur=80
            )
