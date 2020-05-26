
/*
  Tencent is pleased to support the open source community by making Metis available.
  Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
  Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
  https://opensource.org/licenses/BSD-3-Clause
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/

import React from 'react';
import ReactDOM from 'react-dom';
import '../../uw2/index.css';
import settings from './utils/settings.js';
import routerGenerator from './routes';
import pageLoader from './core/builtIn/pageLoader';
import apiLoader from '../../uw-api';
import * as defaultPlugins from '../../uw-plugins';


import '/home/zzy/code/Metis/uweb/src/app.less';


const app = {};


window._g_config = settings.globalConfig;

window.Plugins = defaultPlugins;

const plugins = require('/home/zzy/code/Metis/uweb/src/plugins');
window.Plugins = { ...window.Plugins, ...plugins };




settings.custom = app;

// 注入 API
apiLoader(settings);
// 注入页面加载功能
pageLoader();

const MainRouter = routerGenerator({ ...settings });

ReactDOM.render(
  <MainRouter />,
  document.getElementById('uw-root'),
);
