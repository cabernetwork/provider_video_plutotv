# pylama:ignore=E722
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

import datetime
import time
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import lib.common.utils as utils
from lib.plugins.plugin_epg import PluginEPG

from .translations import plutotv_tv_genres


class EPG(PluginEPG):

    def __init__(self, _instance_obj):
        super().__init__(_instance_obj)
        self.session_token = None

    def dates_to_pull(self):
        """
        Since epg is less than one day, return a forced day item with no
        aging items        
        """
        return [1], []


    def get_boot_data(self, _client_index):
        """
        querys the boot url for the session token
        """
        query_str = {
            'appName':         'web',
            'appVersion':      '9.20.0-89258290264838515e264f5b051b7c1602a58482',
            'deviceVersion':   '148.0.0',
            'deviceModel':     'web',
            'deviceMake':      'firefox',
            'deviceType':      'web',
            'clientModelNumber': '1.0.0',
            'serverSideAds':   'false',
            'drmCapabilities': 'widevine:L3',
            'blockingMode':    '',
            'notificationVersion': '1',
            'appLaunchCount':  '0',
            'lastAppLaunchDate': '',
            'clientID': self.plugin_obj.clientid_list[_client_index]
        }

        header = {
            'user-agent': utils.DEFAULT_USER_AGENT,
            'referer': 'https://pluto.tv/',
            'origin':  'https://pluto.tv',
            'accept':  '*/*',
            'accept-language':  'en-US,en;q=0.9',
            'sec-gpc':          '1',
            'sec-fetch-dest':   'empty',
            'sec-fetch-mode':   'cors',
            'sec-fetch-site':   'same-site',
            'priority':         'u=4'
        }
        uri = self.plugin_obj.unc_plutotv_boot
        boot_json = self.get_uri_data(uri, 2, _params=query_str, _header=header)
        if not boot_json:
            self.logger.notice('{} Failed to retrieve session token'.format(self.plugin_obj.name))
            return
        return boot_json

    def get_time_data(self):
        """
        Returns the start times and durations for upto 2 iterations of epg timelines.
        format is a dict. second times are None if not needed.
        old format is https://api.pluto.tv/v2/channels?start={str(stime.strftime('%Y-%m-%dT%H:00:00.000Z'))}&stop={str(etime.strftime('%Y-%m-%dT%H:00:00.000Z'))}
        """
        # back up 2 hours
        s1_time = datetime.datetime.utcnow()
        # grab day before backing up time!
        day1 = str(s1_time.strftime('%Y-%m-%d'))
        s1_time = (s1_time - datetime.timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
        start1 = str(s1_time.strftime('%Y-%m-%dT%H:00:00.000Z'))

        # get max duration requested
        epg_hours = self.config_obj.data[self.plugin_obj.name.lower()]['epg-hours']
        if epg_hours > 22:
            epg_hours = 16
            self.logger.warning('PlutoTV EPG cannot be more than 22 hours, Recommend changing your settings.  Force using 16.')

        # check if time crosses midnight.  If so, split into two parts
        e2_time = s1_time + datetime.timedelta(hours=epg_hours)
        if s1_time.date() != e2_time.date():
            # crosses midnight
            before_midnight = datetime.time(23, 59, 0)
            e1_time = datetime.datetime.combine(s1_time, before_midnight)
            s2_time = s1_time + datetime.timedelta(days=1)
            midnight = datetime.time(0, 0, 0)
            s2_time = datetime.datetime.combine(s2_time, midnight)
            start2 = str(s2_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
            day2 = str(s2_time.strftime('%Y-%m-%d'))
            e1_duration = int((e1_time - s1_time).total_seconds() / 60)
            e2_duration = int((e2_time - s2_time).total_seconds() / 60)
            return {'day1': day1, 'start1': start1, 'duration1': e1_duration, \
                    'day2': day2, 'start2': start2, 'duration2': e2_duration }
        else:
            e1_duration = int((e2_time - s1_time).total_seconds() / 60)
            return {'day1': day1, 'start1': start1, 'duration1': e1_duration, \
                    'day2': None, 'start2': None, 'duration2': None }

    def get_day_data(self, _ch_id, _start, _duration):
        egp_url = self.plugin_obj.unc_plutotv_epg.format(_start, _ch_id, _duration)
        header = {
            'user-agent': utils.DEFAULT_USER_AGENT,
            'referer': 'https://pluto.tv/',
            'origin':  'https://pluto.tv',
            'authorization': 'Bearer {}'.format(self.session_token)
        }
        return self.get_uri_data(egp_url, 2, _header=header)

    def get_epg_by_day(self, _day, _start, _duration):
        """
        Data is updated in the database.  If an error occurs
        will return False
        """
        try:
            ch_id_list = self.dbchannels.get_channels(self.plugin_obj.name, self.instance_key, _enabled=True).keys()
            boot_data = self.get_boot_data(0)
            self.session_token = boot_data['sessionToken']
            if not self.session_token:
                return False

            program_list = []
            for ch_id in ch_id_list:
                json_data = self.get_day_data(ch_id, _start, _duration)
                time.sleep(1.0)  # timing required by provider
                if not json_data:
                    continue
                json_data = json_data['data']
                if not json_data or len(json_data) < 1:
                    continue
                json_data = json_data[0].get('timelines')
                if not json_data or len(json_data) < 1:
                    continue
                for prog_data in json_data:
                    program_json = self.get_program(ch_id, prog_data)
                    if program_json is not None:
                        program_list.append(program_json)

            if len(program_list) == 0:
                self.logger.debug(
                    '{}:{} Unable to update EPG, no timelines for day {}'
                    .format(self.plugin_obj.name, self.instance_key, _day))
            else:
                self.db.save_program_list(self.plugin_obj.name, self.instance_key, _day, program_list)
                self.logger.info('Refreshed EPG data for {}:{} day {}'
                                  .format(self.plugin_obj.name, self.instance_key, _day))
            return True
        except KeyError as e:
            self.logger.notice('Unable to update PlutoTV EPG, no timelines. Key Error: {}'.format(e))
            self.logger.trace('ch_id: {}   Program Data: {}'.format(ch_id, prog_data))
            return False


    def refresh_programs(self, _epg_day, use_cache=True):
        """
        When multiple days of epg are processed, the _epg_day is used to determine
        which day to process.  Here, we use a duration like 16 hours which may cross
        UTC midnight.  So, multiple days of epg are handled internally.
        """
        time_interval_data = self.get_time_data()
        status = self.get_epg_by_day(time_interval_data['day1'], time_interval_data['start1'], time_interval_data['duration1'])
        if not status:
            # error occurred.  abort processing
            return
        if time_interval_data['day2']:
            self.get_epg_by_day(time_interval_data['day2'], time_interval_data['start2'], time_interval_data['duration2'])
            



    def get_program(self, _ch_id, _program_data):
        # https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd

        # a duration of 0 means dummy program, so skip
        if _program_data['episode']['duration'] == 0:
            return None

        dur_min = int(_program_data['episode']['duration'] / 60 / 1000)

        sid = _ch_id
        start_time = datetime.datetime.fromisoformat(
            _program_data['start'].replace('Z', '+00:00')).timestamp() \
            + self.config_obj.data[self.config_section]['epg-start_adjustment']
        start_time = utils.tm_local_parse(start_time * 1000)
        end_time = datetime.datetime.fromisoformat(
            _program_data['stop'].replace('Z', '+00:00')).timestamp() \
            + self.config_obj.data[self.config_section]['epg-end_adjustment']
        end_time = utils.tm_local_parse(end_time * 1000)
        title = _program_data['title']
        entity_type = None
        prog_id = None

        video_quality = None
        
        cc = False

        live = False
        is_new = False
        if 'liveBroadcast' in _program_data['episode'].keys():
            if _program_data['episode']['liveBroadcast']:
                live = True
                is_new = True

        finale = False
        premiere = False

        air_date = _program_data['episode'].get('firstAired')
        if air_date:
            air_date_msec = datetime.datetime.fromisoformat(
                air_date
                .replace('Z', '+00:00')).timestamp() * 1000
            air_date = utils.date_parse(air_date_msec, '%Y%m%d')
            formatted_date = utils.date_parse(air_date_msec, '%Y/%m/%d')
        else:
            air_date = None
            formatted_date = None

        icon = None
        icon_type = self.config_obj.data[self.plugin_obj.name.lower()]['program_thumbnail']
        if icon_type == 'featuredImage' and \
                icon_type in _program_data['episode']['series'].keys():
            icon = _program_data['episode']['series'][icon_type]['path']
        elif icon_type in _program_data['episode'].keys():
            icon = _program_data['episode'][icon_type]['path']
        elif 'featuredImage' in _program_data['episode']['series'].keys():
            icon = _program_data['episode']['series']['featuredImage']['path']
        elif 'poster' in _program_data['episode'].keys():
            icon = _program_data['episode']['poster']['path']

        if 'rating' in _program_data['episode'].keys():
            rating = _program_data['episode']['rating']
        else:
            rating = None

        if 'genre' in _program_data['episode'].keys():
            genres_orig = _program_data['episode']['genre']
            if genres_orig in plutotv_tv_genres:
                genres = plutotv_tv_genres[genres_orig]
            else:
                self.logger.info(
                    'Missing PlutoTV genre translation for: {}'
                    .format(genres_orig))
                genres = [x.strip() for x in genres_orig.split(' and ')]
        else:
            genres = None
            genres_orig = None

        directors = None
        actors = None
        season = None
        episode = None

        if 'season' in _program_data['episode'].keys():
            if 'number' in _program_data['episode'].keys():
                if _program_data['episode']['season'] == 1 and \
                        _program_data['episode']['number'] < 2:
                    season = None
                    episode = None
                else:
                    season = _program_data['episode']['season']
                    episode = _program_data['episode']['number'] + self.episode_adj
            else:
                season = None
                episode = None
        elif 'number' in _program_data['episode'].keys():
            season = None
            episode = None

        if (season is None) and (episode is None):
            se_common = None
            se_xmltv_ns = None
            se_prog_id = None
        elif (season is not None) and (episode is not None):
            se_common = 'S%02dE%02d' % (season, episode)
            se_xmltv_ns = ''.join([str(season - 1), '.', str(episode - 1), '.0/1'])
            se_prog_id = None

        elif (season is None) and (episode is not None):
            se_common = None
            se_xmltv_ns = None
            se_prog_id = None
        else:  # (season is not None) and (episode is None):
            se_common = 'S%02dE%02d' % (season, 0)
            se_xmltv_ns = ''.join([str(season - 1), '.', '0', '.0/1'])
            se_prog_id = None

        if 'description' not in _program_data['episode'].keys():
            description = 'Unavailable'
        elif not _program_data['episode']['description']:
            description = 'Unavailable None'
        else:
            short_desc = _program_data['episode']['description']
            description = short_desc

        if season is not None:
            subtitle = 'S%02dE%02d ' % (season, episode)
        elif episode is not None:
            subtitle = 'E%02d ' % episode
        else:
            subtitle = ''
        if 'name' in _program_data['episode'].keys():
            subtitle += _program_data['episode']['name']
        else:
            subtitle = None

        json_result = {
            'channel': sid, 'progid': prog_id, 'start': start_time, 'stop': end_time,
            'length': dur_min, 'title': title, 'subtitle': subtitle, 'entity_type': entity_type,
            'desc': description, 'short_desc': short_desc,
            'video_quality': video_quality, 'cc': cc, 'live': live, 'finale': finale,
            'premiere': premiere,
            'air_date': air_date, 'formatted_date': formatted_date, 'icon': icon,
            'rating': rating, 'is_new': is_new, 'genres': genres, 'directors': directors, 'actors': actors,
            'season': season, 'episode': episode, 'se_common': se_common, 'se_xmltv_ns': se_xmltv_ns,
            'se_progid': se_prog_id}
        return json_result
