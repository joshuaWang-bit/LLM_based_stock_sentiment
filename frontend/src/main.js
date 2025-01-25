import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "element-plus/dist/index.css";
import "./style.css";
import App from "./App.vue";

// ECharts
import ECharts from "vue-echarts";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { GaugeChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
} from "echarts/components";

// 注册 ECharts 必要的组件
use([
  CanvasRenderer,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
]);

// 创建Vue应用实例
const app = createApp(App);

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 注册 ECharts 组件
app.component("v-chart", ECharts);

// 使用插件
app.use(createPinia());
app.use(ElementPlus);

// 挂载应用
app.mount("#app");
