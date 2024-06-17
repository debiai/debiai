import services from "../services";

class Data {
  constructor(data) {
    this.categories = data.categories;
    this.labels = data.labels;
    this.nbColumns = data.nbColumns;
    this.nbLinesOriginal = data.nbLines;
    this.sampleIdList = data.sampleIdList;
    this.columns = [];

    // Register the columns
    data.columns.forEach((column) => {
      this.addColumn({
        label: column.label,
        values: column.values,
        category: column.category,
        typeIn: column.type,
        group: column.group,
      });
    });

    this.resetData();
  }

  resetData() {
    this.nbLines = this.nbLinesOriginal;
    this.selectedData = [...Array(this.nbLinesOriginal).keys()];
    this.verticallyUnfoldedColumnsIndexes = []; // Ordered list of unfolded columns
    this.virtualIndexMapping = {}; // Mapping between virtual index and original index

    // Remove any column that was generated by the unfolding
    this.columns.forEach((column) => {
      if (column.unfoldedLevel >= 1) this.removeColumn(column.index);
    });
  }

  columnExists(columnIndex) {
    return this.getColumn(columnIndex) !== undefined;
  }
  currentlyUnfoldedVertically() {
    // Return true if at least one column is unfolded
    return this.verticallyUnfoldedColumnsIndexes?.length > 0;
  }

  // column utils
  getColumn(columnIndex) {
    return this.columns.find((column) => column.index === columnIndex);
  }
  getColumnExistingColumns(columnIndexes) {
    return columnIndexes.map((index) => this.getColumn(index)).filter((column) => column);
  }
  getColumnExistingColumnsLabels(columnIndexes) {
    return this.getColumnExistingColumns(columnIndexes).map((column) => column.label);
  }
  getColumnByLabel(label) {
    return this.columns.find((column) => column.label === label);
  }
  getColumnByLabelAndCategory(label, category) {
    return this.columns.find((column) => column.label === label && column.category === category);
  }

  addColumn({
    label,
    values,
    category,
    typeIn = null,
    group = null,
    unfoldedLevel = 0,
    parentColumnIndex = null,
  }) {
    const columnId = services.uuid();
    this.columns.push(
      new Column(
        this,
        columnId,
        label,
        values,
        category,
        typeIn,
        group,
        unfoldedLevel,
        parentColumnIndex
      )
    );
  }
  removeColumn(columnIndex) {
    this.columns = this.columns.filter((column) => column.index !== columnIndex);
  }

  // Column unfold
  unfoldColumn(columnIndex) {
    if (!this.columnExists(columnIndex)) return;
    if (this.getColumn(columnIndex).typeText === "Dict") this.unfoldHorizontally(columnIndex);
    else if (this.getColumn(columnIndex).typeText === "Array") this.unfoldVertically(columnIndex);
  }
  unfoldVertically(columnIndex) {
    // Add column to the unfolded list
    if (this.verticallyUnfoldedColumnsIndexes.includes(columnIndex)) {
      // Remove it from the unfolded list if it is already unfolded
      this.verticallyUnfoldedColumnsIndexes = this.verticallyUnfoldedColumnsIndexes.filter(
        (index) => index !== columnIndex
      );
    } else this.verticallyUnfoldedColumnsIndexes.push(columnIndex);

    // Set the unfolded column to unfolded
    this.columns.forEach(
      (column) => (column.unfolded = this.verticallyUnfoldedColumnsIndexes.includes(column.index))
    );

    // Update data based on vertical unfold
    if (!this.currentlyUnfoldedVertically()) {
      this.resetData();
      return;
    }

    // Compute the new number of lines and link the virtual index to the original index
    const unfoldedColumn = this.getColumn(this.verticallyUnfoldedColumnsIndexes[0]);
    const virtualIndexMapping = {};
    let nbLines = 0;
    for (let i = 0; i < this.nbLinesOriginal; i++) {
      const value = unfoldedColumn.originalValues[i];
      console.log(value);

      // Check if the value is an array
      if (!Array.isArray(value)) continue;

      // Register the virtual index mapping
      for (let j = 0; j < value.length; j++) {
        virtualIndexMapping[nbLines] = {
          originalIndex: i,
          valueIndex: j,
        };
        nbLines++;
      }
    }

    this.nbLines = nbLines;
    this.selectedData = [...Array(nbLines).keys()];
    this.virtualIndexMapping = virtualIndexMapping;

    console.log("Creating new column");

    // Add the column that is generated by the unfolding
    const column_values = new Array(nbLines).fill(null).map((_, i) => {
      const originalIndex = virtualIndexMapping[i].originalIndex;
      const valueIndex = virtualIndexMapping[i].valueIndex;
      return unfoldedColumn.originalValues[originalIndex][valueIndex];
    });
    const new_label = unfoldedColumn.label + " (unfolded)";
    this.addColumn({
      label: new_label,
      values: column_values,
      category: unfoldedColumn.category,
      typeIn: unfoldedColumn.typeText,
      group: null,
      unfoldedLevel: 1,
      parentColumnIndex: unfoldedColumn.index,
    });
  }
  unfoldHorizontally() {
    // TODO
  }
}

class Column {
  constructor(
    data,
    index,
    label,
    values,
    category,
    typeIn,
    group,
    unfoldedLevel = 0,
    parentColumnIndex = null
  ) {
    this.data = data;
    this.index = index;
    this.label = label;
    this.originalValues = values;
    this.category = category;
    this.group = group;
    this.unfoldedLevel = unfoldedLevel;
    this.parentColumnIndex = parentColumnIndex;
    this.unfolded = false;

    // Override the values with a proxy to handle the unfolding
    this.values = new Proxy(this.originalValues, {
      get: (target, prop) => {
        // Return the value based on the original index
        if (!this.data.currentlyUnfoldedVertically()) {
          if (prop === "length") return this.data.nbLines;
          if (prop === "map") return target.map;
          if (prop === "reduce") return target.reduce;
          return this.originalValues[prop];
        }

        // Return the value based on the virtual index
        if (prop === "length") return this.data.nbLines;
        else if (prop === "map")
          return (callback) => {
            return this.data.selectedData.map((virtualIndex) => {
              return callback(target[this.data.virtualIndexMapping[virtualIndex]].originalIndex);
            });
          };
        else if (prop === "reduce")
          return (callback, initialValue) => {
            return this.data.selectedData.reduce((acc, virtualIndex) => {
              return callback(
                acc,
                target[this.data.virtualIndexMapping[virtualIndex]].originalIndex
              );
            }, initialValue);
          };
        else if (prop === "_isVue") return true;
        else if (prop === "__ob__") return { dep: { id: 0 } };

        if (this.unfoldedLevel > 0) return target[prop];
        return target[this.data.virtualIndexMapping[prop].originalIndex];
      },
    });

    this.defineColumnProperties(typeIn);
  }

  calculateMin(arr) {
    let min = Infinity;
    for (let i = 0; i < arr.length; i++) if (arr[i] < min) min = arr[i];
    return min;
  }
  calculateMax(arr) {
    let max = -Infinity;
    for (let i = 0; i < arr.length; i++) if (arr[i] > max) max = arr[i];
    return max;
  }

  defineColumnProperties(typeIn) {
    // Creating the column object
    this.uniques = [...new Set(this.originalValues)];
    this.nbOccurrence = this.uniques.length;

    // Checking if the this.umn is type text, number or got undefined values
    if (this.uniques.findIndex((v) => v === undefined || v === "" || v === null) >= 0) {
      // undefined Values
      this.type = undefined;
      this.typeText = "undefined";
      this.undefinedIndexes = this.originalValues
        .map((v, i) => (v == undefined || v == "" || v == null ? i : -1))
        .filter((v) => v >= 0);
      console.warn("Undefined values : " + this.label);
      console.warn(this.uniques);
      console.warn(this.originalValues);
    } else if (!(this.uniques.findIndex((v) => !Array.isArray(v)) >= 0)) {
      // If all the values are arrays
      this.type = Array;
      this.typeText = "Array";
    } else if (this.uniques.findIndex((v) => typeof v !== "object")) {
      // If all the values are dictionaries
      this.type = Object;
      this.typeText = "Dict";
    } else if (typeIn === "text" || this.uniques.find((v) => isNaN(v))) {
      // String Values
      this.type = String;
      this.typeText = "Class";
      let tmpUniqMap = {};
      this.valuesIndexUniques = this.uniques.map((str, i) => {
        tmpUniqMap[str] = i;
        return i;
      });

      const _valuesIndex = this.originalValues.map((str) => tmpUniqMap[str]);

      this.valuesIndex = new Proxy(_valuesIndex, {
        get: (target, prop) => {
          // Without unfolding
          if (!this.data.currentlyUnfoldedVertically()) {
            if (prop === "length") return this.data.nbLines;
            if (prop === "map") return target.map;
            if (prop === "reduce") return target.reduce;
            return target[prop];
          }

          // With unfolding
          if (prop === "length") return this.data.nbLines;
          else if (prop === "map")
            return (callback) => {
              return this.data.selectedData.map((virtualIndex) => {
                return callback(target[this.data.virtualIndexMapping[virtualIndex]].originalIndex);
              });
            };
          else if (prop === "reduce")
            return (callback, initialValue) => {
              return this.data.selectedData.reduce((acc, virtualIndex) => {
                return callback(
                  acc,
                  target[this.data.virtualIndexMapping[virtualIndex]].originalIndex
                );
              }, initialValue);
            };
          else if (prop === "_isVue") return true;
          else if (prop === "__ob__") return { dep: { id: 0 } };
          return target[this.data.virtualIndexMapping[prop].originalIndex];
        },
      });

      this.min = this.calculateMin(this.valuesIndexUniques);
      this.max = this.calculateMax(this.valuesIndexUniques);
    } else {
      // Default Type
      this.type = Number;
      this.typeText = "Num";
      this.originalValues = this.originalValues.map((v) => +v);
      this.uniques = this.uniques.map((v) => +v);
      this.nbOccurrence = this.uniques.length;
      this.min = this.calculateMin(this.uniques);
      this.max = this.calculateMax(this.uniques);
      this.average =
        this.originalValues.reduce((a, b) => a + b, 0) / this.originalValues.length || 0;
      if (this.uniques.length < 100) this.uniques.sort((a, b) => a - b);
    }
  }

  updateValues(newValues) {
    this.originalValues = newValues;
    this.defineColumnProperties();
  }
}

export default {
  Data,
  Column,
};
