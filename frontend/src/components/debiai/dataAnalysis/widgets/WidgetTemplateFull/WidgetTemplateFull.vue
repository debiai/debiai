<template>
  <div
    id="WidgetTemplateFull"
    class="dataVisualizationWidget"
  >
    <!-- Multiple columns selection modal -->
    <modal
      v-if="multipleColSelection"
      @close="multipleColSelection = false"
    >
      <ColumnSelection
        v-if="multipleColSelection"
        title="Select columns"
        :data="data"
        :cancelAvailable="selectedColumnsIndexes.length > 0"
        :colorSelection="true"
        :defaultSelected="selectedColumnsIndexes"
        v-on:cancel="multipleColSelection = false"
        v-on:validate="multipleColsSelected"
      />
    </modal>

    <!-- Controls -->
    <div
      id="settings"
      v-if="settings"
    >
      <!-- Columns settings -->
      <div id="columnsSettings">
        <div class="dataGroup">
          <!-- Column selection -->
          <div class="data">
            <div class="name">My column</div>
            <div class="value">
              <ColumnSelectionButton
                :data="data"
                :validColumnsProperties="validColumnsProperties"
                :defaultColumnIndex="selectedColumnIndex"
                title="Select a column"
                v-on:selected="colSelect"
              />
            </div>
          </div>
          <!-- Columns selection -->
          <div class="data">
            <div class="name">My columns</div>
            <div class="value">
              <button @click="multipleColSelection = true">
                {{ selectedColumnsIndexes.length }} col selected
              </button>
            </div>
          </div>
        </div>
        <div class="dataGroup">
          <!-- Checkbox -->
          <div class="data">
            <div class="name">Checkbox</div>
            <div class="value">
              <input
                type="checkbox"
                :id="'checkbox' + index"
                class="customCbx"
                v-model="checkboxValue"
                style="display: none"
              />
              <label
                :for="'checkbox' + index"
                class="toggle"
              >
                <span></span>
              </label>
            </div>
          </div>
          <!-- Selection -->
          <div class="data">
            <div class="name">Selection</div>
            <div class="value">
              <button
                :class="option == 'Opt.1' ? 'radioBtn selected' : 'radioBtn'"
                @click="option = 'Opt.1'"
              >
                Opt.1
              </button>
              <button
                :class="option == 'Opt.2' ? 'radioBtn selected' : 'radioBtn'"
                @click="option = 'Opt.2'"
              >
                Opt.2
              </button>
            </div>
          </div>
          <!-- Input -->
          <div class="data">
            <div class="name">Input</div>
            <div class="value">
              <input
                type="number"
                v-model="value"
                :min="1"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- Display button -->
      <button
        id="displayBtn"
        class="blue"
        @click="display"
      >
        Display
      </button>
    </div>
    <div
      id="content"
      v-if="displayedData"
    >
      {{ displayedData }}
    </div>
  </div>
</template>

<script>
/**
 * Widget Template with full functionality
 * Select only the required ones
 */

// components
import ColumnSelectionButton from "../../common/ColumnSelectionButton";
import ColumnSelection from "../../common/ColumnSelection";

// services
import swal from "sweetalert";

export default {
  components: {
    ColumnSelectionButton,
    ColumnSelection,
  },
  data() {
    return {
      // Settings
      settings: true,

      // Conf
      selectedColumnIndex: null,
      selectedColumnsIndexes: [],
      checkboxValue: true,
      option: "Opt.1",
      value: 0,

      // Other
      multipleColSelection: false,
      displayedData: null,

      // You can add rules on what columns can be selected
      // None of the following properties are required
      validColumnsProperties: {
        // Precise what properties are valid
        // Any column with a property not in the list will be disabled
        // in the column selection modal
        // Except if they are in the `warningTypes` list
        types: ["Class", "Num", "Bool"],

        // Precise what maximum unique values are allowed
        // Any column with more unique values will be disabled
        // in the column selection modal
        maxUniqueValues: 10,

        // Warning types are valid but will be displayed with a warning
        warningTypes: ["Dict", "Array"],

        // Warning maximum unique values
        // Columns with more unique values than this will be displayed with a warning
        // But they will still be selectable
        warningMaxUniqueValues: 5,
      },
    };
  },
  props: {
    data: { type: Object, required: true },
    index: { type: String, required: true },
  },
  created() {
    // Watching for changes from the parent widget

    // Settings btn
    this.$parent.$on("settings", () => {
      this.settings = !this.settings;
    });

    // Redraw btn
    this.$parent.$on("redraw", () => {
      // We draw something again
      this.display();
    });

    // Filters
    this.$parent.$on("filterStarted", () => {});
    this.$parent.$on("filterEnded", () => {});
    this.$parent.$on("filterCleared", () => {});

    // Exporting data
    // You can emit the following event to export and data with an export method
    this.$parent.$emit("setExport", {
      // The only required field is the export type
      type: "MyDataExportType (bounding box, 1Drange, 2Drange, IdList, csv, ...)",

      // Then you can add any data you want, just make sure the object is a valid JSON
      myData1: 0,
      myData2: "data",
      myData3: [null, null, null],
      // ...
    });
  },
  mounted() {
    // Watch for configuration changes
    this.defConfChangeUpdate();
  },
  methods: {
    // ====== Functions defined in the template ===========
    colSelect(index) {
      this.selectedColumnIndex = index;
    },
    multipleColsSelected(indexes) {
      this.selectedColumnsIndexes = indexes;
      this.multipleColSelection = false;
    },
    display() {
      // Do something with the data
      const selectedColumn = this.data.getColumn(this.selectedColumnIndex);
      if (!selectedColumn) return;

      const columnData = this.data.selectedData.map((d) => selectedColumn.values[d]);
      this.displayedData =
        "The first 30 selected values of the chosen column are : " +
        columnData.slice(0, 30).join(", ");

      // We tell the parent that the widget was displayed
      // This will remove some warning and store the current filters
      this.$parent.$emit("drawn");
    },

    // =============== Widget configuration ===============
    /**
     * getConf
     *
     * This optional function can be used to get the configuration of the widget
     * If this function and the setConf function are defined,
     * the blue "save configuration" button will be displayed
     *
     * This function is called when the user clicks on the "save configuration" button
     * it returns the configuration of the widget in an object format
     */
    getConf() {
      let conf = {
        selectedColumn: this.data.getColumn(this.selectedColumnIndex)?.label,
        selectedColumns: this.data.getColumnExistingColumnsLabels(this.selectedColumnsIndexes),
        checkboxValue: this.checkboxValue,
        option: this.option,
        value: this.value,
      };

      return conf;
    },
    /**
     * setConf
     *
     * This optional function can be used to load a saved the configuration
     *
     * This function is called when the user create a widget with a saved configuration
     * it takes in input a previously saved configuration
     *
     * @param {Object} conf - The configuration of the widget
     * @param {Object} options - Options,
     * for example { onStartup: true } if the function is called when the widget is created
     * { onStartup: false } if the function is called when the user loads a configuration
     */
    setConf(conf, options = {}) {
      if (!conf) return;
      if ("selectedColumn" in conf) {
        const c = this.data.getColumnByLabel(conf.selectedColumn);
        if (c) this.selectedColumnIndex = c.index;
        else if (!options.onStartup)
          // Send a warning to the user
          this.$store.commit("sendMessage", {
            title: "warning",
            msg: "The column " + conf.columnX + " hasn't been found",
          });
      }
      if ("selectedColumns" in conf) {
        this.selectedColumnsIndexes = [];
        conf.selectedColumns.forEach((cLabel) => {
          const c = this.data.getColumnByLabel(cLabel);
          if (c) this.selectedColumnsIndexes.push(c.index);
          else if (!options.onStartup)
            this.$store.commit("sendMessage", {
              title: "warning",
              msg: "The column " + cLabel + " hasn't been found",
            });
        });
      }
      if ("checkboxValue" in conf) this.checkboxValue = conf.checkboxValue;
      if ("option" in conf) this.option = conf.option;
      if ("value" in conf) this.value = conf.option;
    },
    /**
     * defConfChangeUpdate
     *
     * This optional function tells the widget that the configuration has changed
     * It will prevent the user to close the widget without saving the configuration
     */
    defConfChangeUpdate() {
      this.$watch(
        (vm) => (
          vm.selectedColumnIndex,
          vm.selectedColumnsIndexes,
          vm.checkboxValue,
          vm.option,
          vm.value,
          Date.now()
        ),
        () => {
          this.$parent.confAsChanged = true;
        }
      );
    },
    /**
     * getConfNameSuggestion
     *
     * This optional function can be used to get the name of the configuration
     */
    getConfNameSuggestion() {
      return "Custom configuration with " + this.data.columns[this.selectedColumnIndex].label;
    },

    // =============== Filtering ===============
    /*
     * If we want to filter the data we can use the following function
     * If this function is defined, the purple "filter" button will be displayed in the widget
     *
     * The filterStarted event is emitted when the filter button is pressed
     * The filterEnded event is emitted when the filter button is pressed again
     * The filterCleared event is emitted when the filter cleared button is pressed
     *
     * See the "created()"
     */
    selectDataOnPlot() {
      if (this.$parent.startFiltering) {
        // The filtering button is active

        let filters = [];

        // Lets filter values on the selected column:
        const selectedValues = [];
        filters.push({
          type: "values",
          columnIndex: this.selectedColumnIndex,
          values: selectedValues,
        });

        // Lets filter intervals on the selected column:
        const min = this.value - 5;
        const max = this.value + 5;
        filters.push({
          type: "intervals",
          columnIndex: this.selectedColumnIndex,
          intervals: [{ min, max }],
        });

        // Apply the filters
        this.$store.commit("addFilters", {
          filters,
          from: {
            widgetType: this.$parent.type,
            widgetName: this.$parent.name,
            widgetIndex: this.index,
          },
          removeExisting: true,
        });
      }
    },

    // =============== Alerting ===============
    /**
     * The swal component is used to display messages and confirmation
     * Refer to https://www.npmjs.com/package/sweetalert
     */
    sendSwal() {
      swal({
        title: "Are you sure?",
        text: "You won't be able to revert this!",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      }).then((validate) => {
        if (validate) {
          // Do something
        }
      });
    },

    // =============== Exporting ==============
    exportJsonWithExportMethods() {
      // You can export data with the export methods
      // More info here : https://debiai.irt-systemx.fr/dashboard/dataExport/#exporting-widget-annotations

      // Set the data that your widget can export with the following line:
      this.$parent.$emit("setExport", {
        foo: "bar",
      });

      // You can clear the data that your widget can export with the following line:
      this.$parent.$emit("setExport", null);
    },
    async getImage() {
      // Return the URL of an image representing this widget results
      // If this widget is a plotly widget, you can use the following function:
      // const plotlyToImage = require("@/services/statistics/analysisExport").plotlyToImage;
      // return await plotlyToImage(this.plotlyDiv);
      // Refer to the other widgets to see how to use it.
    },
  },
  computed: {
    coloredColumnIndex() {
      // Return the index of the column that is colored
      return this.$store.state.StatisticalAnalysis.coloredColumnIndex;
    },
    redrawRequired() {
      return !(this.currentDrawnColorIndex !== this.coloredColumnIndex);
    },
    selectedDataUpdate() {
      return this.data.selectedData;
    },
  },
  watch: {
    selectedDataUpdate() {
      // The selected data have changed
      // We might want to warn the user that an update is required
      this.$parent.selectedDataWarning = true;
      // A redraw btn will be displayed, pressing it will send redraw
      // that can watched and used to redraw a plot (see created())
    },
    redrawRequired: function () {
      // The colored column has changed
      // We cat tell the parent widget that an update is required
      this.$parent.colorWarning = true;
      // A redraw btn will be displayed, pressing it will send redraw
      // that can watched and used to redraw a plot (see created())
    },
  },
};
</script>

<style scoped lang="scss">
#settings {
  display: flex;

  #columnsSettings {
    flex: 1;
    .dataGroup {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;

      .data {
        flex: 1;
        min-width: 200px;

        .value {
          flex: 1;
        }
      }
    }
  }

  button {
    margin: 5px;
  }
}

input {
  width: 100px;
}
</style>
