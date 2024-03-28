<template>
  <div
    id="pointPlot"
    class="dataVisualizationWidget"
  >
    <!-- Settings -->
    <div
      id="settings"
      v-if="settings"
    >
      <!-- Axis selections -->
      <div
        id="axisSelection"
        class="dataGroup"
      >
        <!-- X axis -->
        <div class="data">
          <span class="name">X axis</span>
          <div class="value">
            <Column
              :column="data.columns.find((c) => c.index == columnXindex)"
              :colorSelection="true"
              v-on:selected="xAxisSelection = true"
            />
          </div>
        </div>
        <!-- Swap axis -->
        <button
          class="warning"
          id="swapBtn"
          @click="swap"
        >
          Swap
        </button>
        <!-- Y axis -->
        <div class="data">
          <span class="name">Y axis</span>
          <div class="value">
            <Column
              :column="data.columns.find((c) => c.index == columnYindex)"
              :colorSelection="true"
              v-on:selected="yAxisSelection = true"
            />
          </div>
        </div>
      </div>

      <!-- 2D points & lite plot specific controls -->
      <div id="plotControls">
        <!-- 2D Point Plot Controls -->
        <div
          id="2dPointPlotControls"
          class="dataGroup"
        >
          <!-- Draw -->
          <button
            class="drawBtn blue"
            @click="pointPlot"
            v-if="!pointPlotDrawn"
          >
            Draw 2D points
          </button>
          <button
            class="drawBtn warning"
            @click="clearPointPlot"
            v-else
          >
            Erase 2D points
          </button>
          <!-- Point size axis -->
          <div class="data">
            <span class="name">Point size axis</span>
            <div
              class="value"
              v-if="columnSizeIndex !== null"
            >
              <Column
                :column="data.columns.find((c) => c.index == columnSizeIndex)"
                :colorSelection="true"
                v-on:selected="sizeAxisSelection = true"
              />
              <button
                class="red"
                @click="
                  columnSizeIndex = null;
                  pointPlotDrawn = false;
                "
              >
                Remove
              </button>
            </div>
            <div
              class="value"
              v-else
            >
              <button @click="sizeAxisSelection = true">Select an axis</button>
            </div>
          </div>
          <!-- Max point Size -->
          <div
            class="data"
            v-if="columnSizeIndex !== null"
          >
            <span class="name">Max point Size</span>
            <div class="value">
              <input
                type="number"
                v-model="maxPointSize"
                :min="1"
                :step="5"
                @change="pointPlotDrawn = false"
              />
            </div>
          </div>
          <!-- Point opacity -->
          <div class="data">
            <span class="name">Point opacity</span>
            <div class="value">
              Auto:
              <input
                type="checkbox"
                v-model="autoPointOpacity"
              />
              <input
                type="number"
                v-if="!autoPointOpacity"
                v-model="pointOpacity"
                :step="0.05"
                :min="0.01"
                :max="1"
              />
              <div
                v-else
                style="padding-left: 10px"
              >
                {{ Math.round(pointOpacity * 1000) / 1000 }}
              </div>
            </div>
          </div>
        </div>

        <!-- Line Plot Controls -->
        <div
          id="linePlotControls"
          class="dataGroup"
        >
          <!-- Draw -->
          <button
            class="drawBtn blue"
            @click="checkLinePlot"
            v-if="!linePlotDrawn"
          >
            Draw statistics
          </button>
          <button
            v-else
            class="drawBtn warning"
            @click="clearLinePlot"
          >
            Clear statistics
          </button>
          <!-- Bins -->
          <div class="data">
            <span class="name">Bins</span>
            <div class="value">
              <input
                type="number"
                v-model="bins"
                :min="1"
                @change="linePlotDrawn = false"
              />
            </div>
          </div>
          <!-- Display average as bar -->
          <div class="data">
            <span class="name">Display as bar</span>
            <div class="value">
              <input
                type="checkbox"
                :id="'averageAsBar' + index"
                class="customCbx"
                style="display: none"
                v-model="averageAsBar"
              />
              <label
                :for="'averageAsBar' + index"
                class="toggle"
              >
                <span></span>
              </label>
            </div>
          </div>
          <!-- Display null values -->
          <div
            class="data"
            v-if="!averageAsBar"
          >
            <span class="name">Display null values</span>
            <div class="value">
              <input
                type="checkbox"
                :id="'displayNull' + index"
                class="customCbx"
                style="display: none"
                v-model="displayNull"
                @change="updateTraces()"
              />
              <label
                :for="'displayNull' + index"
                class="toggle"
              >
                <span></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 2D points & lite plot common controls -->
      <div
        id="commonControls"
        class="dataGroup"
      >
        <!-- Group by color -->
        <div
          class="data"
          v-if="coloredColumnIndex != null"
        >
          <span class="name">Group by color</span>
          <div class="value">
            <input
              type="checkbox"
              :id="'dividePerColorCbxPointPlot' + index"
              class="customCbx"
              v-model="dividePerColor"
              style="display: none"
            />
            <label
              :for="'dividePerColorCbxPointPlot' + index"
              class="toggle"
            >
              <span></span>
            </label>
          </div>
        </div>
        <!-- Absolute value -->
        <div class="data">
          <span class="name">Absolute value</span>
          <div class="value">
            <input
              type="checkbox"
              :id="'absolute' + index"
              class="customCbx"
              v-model="absolute"
              style="display: none"
            />
            <label
              :for="'absolute' + index"
              class="toggle"
            >
              <span></span>
            </label>
          </div>
        </div>
        <!-- Fixe ranges -->
        <button
          style="margin: 2px"
          class="warning"
          @click="axisRangeModal = !axisRangeModal"
          v-if="!axisXAuto || !axisYAuto"
        >
          Edit the axis ranges
        </button>
        <button
          style="margin: 2px"
          @click="axisRangeModal = !axisRangeModal"
          v-else
        >
          Set the axis ranges
        </button>
      </div>
    </div>

    <!-- Modals -->
    <!-- Xcol selection -->
    <modal
      v-if="xAxisSelection"
      @close="xAxisSelection = false"
    >
      <ColumnSelection
        title="Select the X axis"
        :data="data"
        :validateRequired="false"
        :colorSelection="true"
        :defaultSelected="[columnXindex]"
        v-on:cancel="xAxisSelection = false"
        v-on:colSelect="xAxisSelect"
      />
    </modal>
    <!-- Ycol selection -->
    <modal
      v-if="yAxisSelection"
      @close="yAxisSelection = false"
    >
      <ColumnSelection
        title="Select the Y axis"
        :data="data"
        :validateRequired="false"
        :colorSelection="true"
        :defaultSelected="[columnYindex]"
        v-on:cancel="yAxisSelection = false"
        v-on:colSelect="yAxisSelect"
      />
    </modal>
    <!-- Size axis selection -->
    <modal
      v-if="sizeAxisSelection"
      @close="sizeAxisSelection = false"
    >
      <ColumnSelection
        title="Select the point size axis"
        :data="data"
        :validateRequired="false"
        :colorSelection="true"
        :defaultSelected="columnSizeIndex === null ? undefined : [columnSizeIndex]"
        v-on:cancel="sizeAxisSelection = false"
        v-on:colSelect="sizeAxisSelect"
      />
    </modal>
    <!-- Axis range selection -->
    <modal
      @close="axisRangeModal = false"
      v-if="axisRangeModal"
    >
      <AxisRangeSelection
        :index="index"
        :axisXAuto="axisXAuto"
        :axisYAuto="axisYAuto"
        :axisXMin="axisXMin"
        :axisXMax="axisXMax"
        :axisYMin="axisYMin"
        :axisYMax="axisYMax"
        v-on:cancel="axisRangeModal = false"
        v-on:apply="axisRangeSelect"
      />
    </modal>

    <!-- The plotly plot -->
    <div
      class="plot"
      :id="'PPDiv' + index"
    ></div>
  </div>
</template>

<script>
import Plotly from "plotly.js/dist/plotly";
import { plotlyToImage } from "@/services/statistics/analysisExport";

// components
import ColumnSelection from "../../common/ColumnSelection";
import Column from "../../common/Column";
import AxisRangeSelection from "../../common/AxisRangeSelection";

// services
import dataOperations from "@/services/statistics/dataOperations";
import swal from "sweetalert";

export default {
  components: {
    ColumnSelection,
    Column,
    AxisRangeSelection,
  },
  data() {
    return {
      // === Setting ===
      settings: true,
      xAxisSelection: false,
      yAxisSelection: false,
      sizeAxisSelection: false,
      axisRangeModal: false,

      // === Configuration ===
      // Axis
      columnXindex: 0,
      columnYindex: 0,
      // Shared settings
      dividePerColor: true,
      absolute: false,
      // 2d point plot settings
      autoPointOpacity: true,
      pointOpacity: null,
      columnSizeIndex: null,
      maxPointSize: 50,
      // Line plot settings
      averageAsBar: false,
      displayNull: true,
      bins: 0,
      // Axis range
      axisXAuto: true,
      axisXMin: 0,
      axisXMax: 1,
      axisYAuto: true,
      axisYMin: 0,
      axisYMax: 1,

      // === Other ===
      pointPlotDrawn: false,
      linePlotDrawn: false,
      currentDrawnColorIndex: null,
    };
  },
  props: {
    data: { type: Object, required: true },
    index: { type: String, required: true },
    selectedData: { type: Array, required: true },
  },
  created() {
    // Widget setting btn
    this.$parent.$on("settings", () => {
      this.settings = !this.settings;
      window.dispatchEvent(new Event("resize"));
    });

    // Widget redraw btn
    this.$parent.$on("redraw", this.updateTraces);

    // Filters
    this.$parent.$on("filterStarted", this.filterStarted);
    this.$parent.$on("filterEnded", this.filterEnded);
    this.$parent.$on("filterCleared", this.filterCleared);
  },
  mounted() {
    this.divPointPlot = document.getElementById("PPDiv" + this.index);
    this.xAxisSelect(0);
    this.yAxisSelect(1);
    this.setPointOpacity();

    // Watch for configuration changes
    this.defConfChangeUpdate();
  },
  methods: {
    // Conf
    getConf() {
      let conf = {
        // Axis
        columnX: this.data.columns[this.columnXindex].label,
        columnY: this.data.columns[this.columnYindex].label,
        // Shared settings
        dividePerColor: this.dividePerColor,
        absolute: this.absolute,
        // 2d point plot settings
        autoPointOpacity: this.autoPointOpacity,
        // Line plot settings
        averageAsBar: this.averageAsBar,
        bins: this.bins,
      };

      if (!this.averageAsBar) conf.displayNull = this.displayNull;
      if (!this.autoPointOpacity) conf.pointOpacity = this.pointOpacity;
      if (this.columnSizeIndex !== null) {
        conf.maxPointSize = this.maxPointSize;
        conf.columnSized = this.data.columns[this.columnSizeIndex].label;
      }

      // Set axis range
      if (!this.axisXAuto) {
        conf.axisXMin = this.axisXMin;
        conf.axisXMax = this.axisXMax;
      }
      if (!this.axisYAuto) {
        conf.axisYMin = this.axisYMin;
        conf.axisYMax = this.axisYMax;
      }

      return conf;
    },
    setConf(conf, options = {}) {
      if (!conf) return;

      if ("columnX" in conf) {
        let c = this.data.columns.find((c) => c.label == conf.columnX);
        if (c) this.columnXindex = c.index;
        else
          this.$store.commit("sendMessage", {
            title: "warning",
            msg: "The column " + conf.columnX + " hasn't been found",
          });
      }
      if ("columnY" in conf) {
        let c = this.data.columns.find((c) => c.label == conf.columnY);
        if (c) this.columnYindex = c.index;
        else
          this.$store.commit("sendMessage", {
            title: "warning",
            msg: "The column " + conf.columnY + " hasn't been found",
          });
      }
      if ("columnSized" in conf) {
        let c = this.data.columns.find((c) => c.label == conf.columnSized);
        if (c) this.columnSizeIndex = c.index;
        else
          this.$store.commit("sendMessage", {
            title: "warning",
            msg: "The column " + conf.columnSized + " hasn't been found",
          });
      }
      if ("absolute" in conf) this.absolute = conf.absolute;
      if ("autoPointOpacity" in conf) this.autoPointOpacity = conf.autoPointOpacity;
      if ("pointOpacity" in conf) this.pointOpacity = conf.pointOpacity;
      if ("columnSizeIndex" in conf) this.columnSizeIndex = conf.columnSizeIndex;
      if ("maxPointSize" in conf) this.maxPointSize = conf.maxPointSize;
      if ("averageAsBar" in conf) this.averageAsBar = conf.averageAsBar;
      if ("displayNull" in conf) this.displayNull = conf.displayNull;
      if ("bins" in conf) this.bins = conf.bins;
      if ("dividePerColor" in conf) this.dividePerColor = conf.dividePerColor;
      if ("axisXMin" in conf) {
        this.axisXAuto = false;
        this.axisXMin = conf.axisXMin;
      }
      if ("axisXMax" in conf) {
        this.axisXAuto = false;
        this.axisXMax = conf.axisXMax;
      }
      if ("axisYMin" in conf) {
        this.axisYAuto = false;
        this.axisYMin = conf.axisYMin;
      }
      if ("axisYMax" in conf) {
        this.axisYAuto = false;
        this.axisYMax = conf.axisYMax;
      }

      if (options.onStartup !== true) this.settings = true;
    },
    defConfChangeUpdate() {
      this.$watch(
        (vm) => (
          vm.columnXindex,
          vm.columnYindex,
          vm.dividePerColor,
          vm.absolute,
          vm.autoPointOpacity,
          vm.pointOpacity,
          vm.columnSizeIndex,
          vm.maxPointSize,
          vm.averageAsBar,
          vm.displayNull,
          vm.bins,
          vm.axisXAuto,
          vm.axisXMin,
          vm.axisXMax,
          vm.axisYAuto,
          vm.axisYMin,
          vm.axisYMax,
          Date.now()
        ),
        () => {
          this.$parent.confAsChanged = true;
        }
      );
    },
    getConfNameSuggestion() {
      let confName =
        this.data.columns[this.columnXindex].label +
        " / " +
        this.data.columns[this.columnYindex].label;

      // Add the sized column to the legend name
      if (this.columnSizeIndex !== null)
        confName += " Sized by " + this.data.columns[this.columnSizeIndex].label;

      // Add if y is absolute
      if (this.absolute) confName += " (abs)";

      return confName;
    },

    // Plot
    updateTraces() {
      if (this.pointPlotDrawn) this.pointPlot();
      if (this.linePlotDrawn) this.checkLinePlot();
    },

    // Point plot
    pointPlot() {
      let colX = this.data.columns[this.columnXindex];
      let colY = this.data.columns[this.columnYindex];

      // Apply selection
      let valuesX = this.selectedData.map((i) => colX.values[i]);
      let valuesY;
      if (colY.type == String) valuesY = this.selectedData.map((i) => colY.valuesIndex[i]);
      else valuesY = this.selectedData.map((i) => colY.values[i]);

      // Abs checked
      if (this.absolute) valuesY = valuesY.map((val) => Math.abs(val));

      // Color
      let colorscale = "Portland";
      let showscale = false;
      let color = 0;
      let cmin;
      let cmax;

      let colColor;
      if (this.coloredColumnIndex !== null && this.dividePerColor) {
        colColor = this.data.columns[this.coloredColumnIndex];
        color = this.selectedData.map((i) =>
          colColor.type == String ? colColor.valuesIndex[i] : colColor.values[i]
        );
        // Deal with color if string
        if (colColor.type === String) {
          cmin = Math.min(...colColor.valuesIndexUniques);
          cmax = Math.max(...colColor.valuesIndexUniques);
        } else {
          showscale = true;
          cmin = colColor.min;
          cmax = colColor.max;
        }
      }

      // Size
      let size;
      let valueMin;
      let valueMax;
      const MIN_POINT_SIZE = 3;
      let colSize;
      if (this.columnSizeIndex !== null) {
        colSize = this.data.columns[this.columnSizeIndex];
        size = this.selectedData.map((i) =>
          colSize.type == String ? colSize.valuesIndex[i] : colSize.values[i]
        );
        if (colSize.type === String) {
          valueMax = colSize.valuesIndexUniques.length - 1;
        } else {
          valueMin = colSize.min;
          valueMax = colSize.max;
          size = size.map((s) => s - valueMin);
        }
        let ratio = (this.maxPointSize - MIN_POINT_SIZE) / valueMax;
        size = size.map((s) => MIN_POINT_SIZE + ratio * s);
      }

      // Assembling the plotly trace
      let pointData = {
        x: valuesX,
        y: valuesY,
        name: "Points",
        mode: "markers",
        type: "scattergl",
        marker: {
          cmin,
          cmax,
          opacity: this.pointOpacity,
          color,
          colorscale,
          showscale,
          size,
          line: {
            // Don't show the border
            width: 0,
          },
        },
      };

      let layout = this.generateLayout({ colX, colY, colColor, colSize });

      // Draw
      this.clearPointPlot();
      if (this.linePlotDrawn) {
        Plotly.addTraces(this.divPointPlot, [pointData], 0);
        this.updateLayout(layout);
      } else this.drawPlot([pointData], layout); // regenerate or generate plot

      this.pointPlotDrawn = true;
      this.$parent.$emit("drawn");
      this.currentDrawnColorIndex = this.coloredColumnIndex;
    },
    clearPointPlot() {
      // remove the first trace
      if (!this.linePlotDrawn) Plotly.purge(this.divPointPlot);
      else {
        let tracesToDelete = [];
        this.divPointPlot.data.forEach((trace, i) => {
          if (trace.name === "Points" && trace.mode === "markers") tracesToDelete.push(i);
        });

        Plotly.deleteTraces(this.divPointPlot, tracesToDelete);
      }
      this.pointPlotDrawn = false;
    },

    // Line plot
    checkLinePlot() {
      if (!this.dividePerColor || this.coloredColumnIndex == null) {
        this.linePlot();
        return;
      }

      // Check that the group by color is not to performance intensive
      let colColor = this.data.columns[this.coloredColumnIndex];

      if (colColor.uniques.length <= 100) {
        this.linePlot();
        return;
      }

      // If it is, ask for confirmation
      swal({
        title: "Long calculation: do you want to proceed ?",
        text: "Point plot: You appear to have selected more than 100 uniques color values. This may take a while !",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      }).then((validate) => {
        if (validate) this.linePlot();
      });
    },

    // Check columns type and uniques values
    async DoesUserAcceptRisk() {
      let colX = this.data.columns[this.columnXindex];
      let colY = this.data.columns[this.columnYindex];
      let uniquesValX = colX.uniques.length;
      let uniquesValY = colY.uniques.length;

      let warningMessage = "";

      if (colX.type == String && uniquesValX > 1000) {
        warningMessage += "The column X has more than 1000 uniques values\n";
      }

      if (colY.type == String && uniquesValY > 100) {
        warningMessage += "The column Y has more than 100 uniques values\n";
      }

      if (warningMessage == "") return true;

      const rep = await swal({
        title: "Warning",
        text: warningMessage,
        icon: "warning",
        buttons: true,
        dangerMode: true,
      });

      return rep == true;
    },

    async linePlot() {
      // Apply selection
      let traces = [];
      let colX = this.data.columns[this.columnXindex];
      let valuesX;
      if (colX.type == String) valuesX = this.selectedData.map((i) => colX.valuesIndex[i]);
      else valuesX = this.selectedData.map((i) => colX.values[i]);

      let colY = this.data.columns[this.columnYindex];
      let valuesY;
      if (colY.type == String) valuesY = this.selectedData.map((i) => colY.valuesIndex[i]);
      else valuesY = this.selectedData.map((i) => colY.values[i]);

      // Abs checked
      if (this.absolute) valuesY = valuesY.map((val) => Math.abs(val));

      let colColor = this.data.columns[this.coloredColumnIndex];
      if (colColor && this.dividePerColor) {
        // === Divide lines per color ===
        let selectedColorsValues =
          colColor.type == String
            ? this.selectedData.map((i) => colColor.valuesIndex[i])
            : this.selectedData.map((i) => colColor.values[i]);
        let selectorUniques =
          colColor.type == String ? colColor.valuesIndexUniques : colColor.uniques;

        let groupedValues = dataOperations.groupBy(selectedColorsValues, selectorUniques);

        let fromIn = dataOperations.getMin(valuesX);
        let toIn = dataOperations.getMax(valuesX);

        groupedValues.forEach((idValues, colColorUniqueId) => {
          let stats = dataOperations.getStats(
            idValues.map((i) => valuesX[i]),
            idValues.map((i) => valuesY[i]),
            this.bins - 1,
            {
              fromIn,
              toIn,
              detailed: false,
              displayNull: this.displayNull,
            }
          );

          if (colX.type == String) {
            stats.xSections = stats.xSections.map(
              (v, i) => colX.uniques[Math.floor(i * (colX.uniques.length / this.bins))]
            );
          }

          traces.push({
            name: String(colColor.uniques[colColorUniqueId]),
            x: stats.xSections,
            y: stats.average,
            type: this.averageAsBar ? "bar" : "scattergl",
            mode: "lines",
            line: {
              // color:
              //   colColor.type == String
              //     ? colColor.valuesIndexUniques[colColorUniqueId]
              //     : colColor.uniques[colColorUniqueId],
              width: 3,
              shape: "spline",
            },
          });
        });
      } else {
        let colY = this.data.columns[this.columnYindex];
        if (colY.type == String) this.valuesY = this.selectedData.map((i) => colY.valuesIndex[i]);

        let stats = dataOperations.getStats(valuesX, valuesY, this.bins - 1, {
          displayNull: this.displayNull,
        });

        if (colX.type == String) {
          stats.xSections = stats.xSections.map(
            (v, i) => colX.uniques[Math.floor(i * (colX.uniques.length / this.bins))]
          );
        }

        traces = [
          {
            x: stats.xSections,
            y: stats.average,
            mode: "lines",
            type: this.averageAsBar ? "bar" : "scattergl",
            name: "Average",
            line: { color: "red", width: 5, shape: "spline" },
            marker: { color: "#ff5869" },
          },
          {
            x: stats.xSections,
            y: stats.average,
            type: "scattergl",
            mode: "lines",
            name: "STD",
            line: { color: "red", width: 0, shape: "spline" },
            error_y: {
              type: "data",
              array: stats.std,
              visible: true,
            },
            visible: "legendonly",
          },
          {
            x: stats.xSections,
            y: stats.max,
            type: "scattergl",
            mode: "lines",
            name: "Max",
            line: { color: "blue" },
            visible: "legendonly",
          },
          {
            x: stats.xSections,
            y: stats.min,
            mode: "lines",
            type: "scattergl",
            name: "Min",
            line: { color: "blue", shape: "spline" },
            visible: "legendonly",
          },
          {
            x: stats.xSections,
            y: stats.q1,
            mode: "lines",
            type: "scattergl",
            name: "Third decile",
            line: { color: "purple", shape: "spline" },
            visible: "legendonly",
          },
          {
            x: stats.xSections,
            y: stats.q3,
            mode: "lines",
            type: "scattergl",
            name: "First decile",
            line: { color: "purple", shape: "spline" },
            visible: "legendonly",
          },
        ];
      }

      let layout = this.generateLayout({ colX, colY, colColor });

      this.clearLinePlot();
      if (this.pointPlotDrawn) {
        Plotly.addTraces(this.divPointPlot, traces);
        this.updateLayout(layout);
      } else this.drawPlot(traces, layout); // regenerate or generate plot

      this.linePlotDrawn = true;
      this.$parent.$emit("drawn");
      this.currentDrawnColorIndex = this.coloredColumnIndex;
    },
    clearLinePlot() {
      // Remove the last two traces
      if (!this.pointPlotDrawn) Plotly.purge(this.divPointPlot);
      else {
        let tracesToDelete = [];
        this.divPointPlot.data.forEach((trace, i) => {
          if (trace.name !== "Points" && trace.mode == "lines") tracesToDelete.push(i);
        });

        Plotly.deleteTraces(this.divPointPlot, tracesToDelete);
      }
      this.linePlotDrawn = false;
    },

    // Draw
    generateLayout({ colX, colY, colColor, colSize }) {
      let layout = {
        title: "<b>" + colX.label + "</b> / <b>" + colY.label + "</b>",
        xaxis: {
          title: {
            text: colX.label,
          },
        },
        yaxis: {
          title: {
            text: colY.label,
          },
        },
        margin: {
          l: 50,
          r: 20,
          b: 50,
          t: 50,
        },

        // Dragmode for the filtering
        dragmode: this.$parent.startFiltering ? "select" : "zoom",
      };

      // Add the color to the legend name
      if (this.dividePerColor && colColor)
        layout.title += " Grouped by <b>" + colColor.label + "</b>";

      // Add the sized column to the legend name
      if (this.columnSizeIndex !== null && colSize)
        layout.title += " Sized by <b>" + colSize.label + "</b>";

      // Add if y is absolute
      if (this.absolute) layout.yaxis.title.text += " (absolute value)";

      // Set y axis label text if string
      if (colY.type == String) {
        layout.yaxis.tickvals = colY.valuesIndexUniques;
        layout.yaxis.ticktext = colY.uniques;
      }

      return layout;
    },
    updateLayout(layout) {
      Plotly.relayout(this.divPointPlot, {
        title: layout.title,
        "yaxis.title.text": layout.yaxis.title.text,
      });
    },
    drawPlot(traces, layout) {
      // Apply range if needed
      if (!this.axisXAuto) layout.xaxis.range = [this.axisXMin, this.axisXMax];
      if (!this.axisYAuto) layout.yaxis.range = [this.axisYMin, this.axisYMax];

      // Draw the plot
      Plotly.react(this.divPointPlot, traces, layout, {
        responsive: true,
        displayModeBar: false,
      });

      // Set zoom events for the data filtering
      this.divPointPlot.removeListener("plotly_selected", this.selectDataOnPlot);
      this.divPointPlot.on("plotly_selected", this.selectDataOnPlot);
    },

    // Filters
    selectDataOnPlot(event) {
      if (!this.$parent.startFiltering) return;

      // Clear the export
      this.$parent.$emit("setExport", null);

      // An event msg :
      // {
      //   points: ...,
      //   selections: [{
      //     x0: ...,
      //     x1: ...,
      //     y0: ...,
      //     y1: ...,
      //     ...
      //  }] // One per rectangles
      //  range: { x : [min, max], y : [min, max] }
      // }
      // or undefined (single click or double click out)
      // or { points: [], selections: [] } (double click in)
      if (!event || !event.selections || event.selections.length === 0) {
        this.$store.commit("addFilters", {
          filters: [],
          from: {
            widgetType: this.$parent.type,
            widgetName: this.$parent.name,
            widgetIndex: this.index,
          },
          removeExisting: true,
        });
        this.$parent.$emit("setExport", null);
        Plotly.relayout(this.divPointPlot, { shapes: [] }); // Rectangle
        return;
      }

      // Create the filters
      let colx = this.data.columns[this.columnXindex];
      let coly = this.data.columns[this.columnYindex];

      // Create the first filter
      const selections = event.selections;
      const filters = [
        this.getFilterFromColumn(colx, selections[0].x0, selections[0].x1, false),
        this.getFilterFromColumn(coly, selections[0].y1, selections[0].y0, this.absolute),
      ];

      // Store the filters in the DebiAI selection system
      this.$store.commit("addFilters", {
        filters,
        from: {
          widgetType: this.$parent.type,
          widgetName: this.$parent.name,
          widgetIndex: this.index,
        },
        removeExisting: true,
      });

      // Exporting the boundaries of the selections with the export feature
      // Exporting only the first selection TODO : add all the selections
      // Goal format :
      // {
      //   type: "2Drange",
      //   colX : colName
      //   colY : colName
      //   x : [min, max],
      //   y : [min, max]
      // }

      const getRangeFromFilter = (filter) => {
        if (filter.type == "values")
          return [filter.values[0], filter.values[filter.values.length - 1]];
        else if (filter.type == "intervals")
          return [filter.intervals[0].min, filter.intervals[0].max];
        return null;
      };
      const rangeX = getRangeFromFilter(filters[0]);
      const rangeY = getRangeFromFilter(filters[1]);

      const exportData = {
        type: "2Drange",
        colX: colx.label,
        colY: coly.label,
        x: rangeX,
        y: rangeY,
      };

      this.$parent.$emit("setExport", exportData);
    },
    getFilterFromColumn(col, min, max, absolute) {
      // Create a debiai filter from a column and a range

      // Filter format :
      // [
      //   {
      //     "type": "values",
      //     "values": [
      //       "image-1",
      //       "image-3",
      //       ...
      //     ],
      //     "columnIndex": 0
      //   },
      //   {
      //     "type": "intervals",
      //     "intervals": [
      //       {
      //        max: 19.950596252129472,
      //        min: 6.730834752981263
      //       }
      //     ],
      //     "columnIndex": 1
      //   }
      // ]

      // Fix the fact that the min and max may be inverted
      if (min > max) {
        let tmp = min;
        min = max;
        max = tmp;
      }

      if (col.type !== String) {
        if (absolute) {
          return {
            type: "intervals",
            intervals: [
              { min, max },
              { max: -min, min: -max },
            ],
            columnIndex: col.index,
          };
        } else {
          return {
            type: "intervals",
            intervals: [{ min, max }],
            columnIndex: col.index,
          };
        }
      } else {
        let selectedUniquesValuesIndex = col.valuesIndexUniques.filter((v) => v >= min && v <= max);
        let selectedValues = selectedUniquesValuesIndex.map((v) => col.uniques[v]);

        // Quick fix for the case of timestamps
        if (selectedValues.length == 0) selectedValues = [min, max];

        return {
          type: "values",
          values: selectedValues,
          columnIndex: col.index,
        };
      }
    },
    filterStarted() {
      // Set the layout on select mod
      if (this.pointPlotDrawn || this.linePlotDrawn)
        Plotly.relayout(this.divPointPlot, { dragmode: "select" });
    },
    filterEnded() {
      // Remove the layout select mod
      if (this.pointPlotDrawn || this.linePlotDrawn)
        Plotly.relayout(this.divPointPlot, { dragmode: "zoom" });

      this.$parent.$emit("setExport", null);
    },
    filterCleared() {
      // Remove the selection on the plot
      if (this.pointPlotDrawn || this.linePlotDrawn)
        Plotly.restyle(this.divPointPlot, "selectedpoints", null);

      this.$parent.$emit("setExport", null);
    },

    // Axis selection
    async xAxisSelect(index) {
      // Check that columns won't result in a performance issue
      const userAccept = await this.DoesUserAcceptRisk();
      if (!userAccept) return;

      this.columnXindex = index;
      this.xAxisSelection = false;
      this.pointPlotDrawn = false;
      this.linePlotDrawn = false;
      this.setBins();
    },
    async yAxisSelect(index) {
      // Check that columns won't result in a performance issue
      const userAccept = await this.DoesUserAcceptRisk();
      if (!userAccept) return;

      this.columnYindex = index;
      this.yAxisSelection = false;
      this.pointPlotDrawn = false;
      this.linePlotDrawn = false;
    },
    sizeAxisSelect(index) {
      this.columnSizeIndex = index;
      this.sizeAxisSelection = false;
      this.pointPlotDrawn = false;
    },
    async swap() {
      const userAccept = await this.DoesUserAcceptRisk();
      if (!userAccept) return;

      let memoryLinePlotDrawn = this.linePlotDrawn;
      let temp = this.columnYindex;
      this.columnYindex = this.columnXindex;
      this.columnXindex = temp;
      this.setBins();

      this.linePlotDrawn = memoryLinePlotDrawn;
      this.updateTraces();
    },
    setBins() {
      let colX = this.data.columns[this.columnXindex];
      if (colX.type == String) this.bins = Math.min(colX.nbOccurrence, 300);
      else this.bins = Math.min(colX.nbOccurrence, 30);
      this.linePlotDrawn = false;
    },
    setPointOpacity() {
      this.pointOpacity = parseFloat((1 / Math.pow(this.selectedData.length, 0.2)).toFixed(2));
    },
    axisRangeSelect({ axisXAuto, axisXMin, axisXMax, axisYAuto, axisYMin, axisYMax }) {
      this.axisRangeModal = false;
      this.pointPlotDrawn = false;
      this.linePlotDrawn = false;
      this.axisXAuto = axisXAuto;
      this.axisXMin = axisXMin;
      this.axisXMax = axisXMax;
      this.axisYAuto = axisYAuto;
      this.axisYMin = axisYMin;
      this.axisYMax = axisYMax;
    },

    // Export
    async getImage() {
      // Return the URL of an image representing this widget results
      return await plotlyToImage(this.divPointPlot);
    },
  },
  computed: {
    coloredColumnIndex() {
      return this.$store.state.StatisticalAnalysis.coloredColumnIndex;
    },
    redrawRequired() {
      return !(this.currentDrawnColorIndex !== this.coloredColumnIndex);
    },
  },
  watch: {
    dividePerColor: function () {
      this.updateTraces();
    },
    autoPointOpacity: function (newVal) {
      if (newVal) this.setPointOpacity();
    },
    pointOpacity: function () {
      this.pointPlotDrawn = false;
    },
    absolute: function () {
      this.updateTraces();
    },
    displayNull: function () {
      if (this.linePlotDrawn) this.checkLinePlot();
    },
    averageAsBar: function () {
      if (this.linePlotDrawn) this.checkLinePlot();
    },
    selectedData: function () {
      if (!this.$parent.startFiltering && (this.pointPlotDrawn || this.linePlotDrawn))
        this.$parent.selectedDataWarning = true;
    },
    redrawRequired(o, n) {
      this.$parent.colorWarning = n;
    },
  },
};
</script>

<style scoped>
#pointPlot {
  display: flex;
  flex-direction: column;
}

/* axisSelection */
#axisSelection {
  flex-wrap: wrap;
}

#axisSelection .data {
  flex: 1;
}

#axisSelection .data .value {
  flex: 1;
}

#axisSelection #swapBtn {
  margin: 0 10px 0 10px;
}

/* plotControls */
#plotControls {
  display: flex;
  flex-wrap: wrap;
}

#plotControls .dataGroup {
  flex: 1;
  flex-direction: column;
  justify-content: flex-start;
  min-width: 300px;
}

#plotControls .drawBtn {
  height: 40px;
}

#plotControls .data {
  margin-top: 3px;
  min-height: 35px;
}

#plotControls .data .name {
  flex: 0.4;
}

#plotControls .data .value {
  flex: 1;
}

/* commonControls */
#commonControls {
  justify-content: space-evenly;
  flex-wrap: wrap;
}

#commonControls .data {
  min-height: 35px;
}

input[type="number"] {
  width: 70px;
}
</style>
