<template>
  <div id="ColumnUnfoldingMenu">
    <!-- Vertical or horizontal unfolding menu -->
    <Modal
      @close="columnToUnfoldVerticallyOrHorizontally = null"
      v-if="columnToUnfoldVerticallyOrHorizontally"
    >
      <div id="verticalOrHorizontalUnfoldingMenu">
        <h3
          class="aligned spaced"
          style="gap: 20px"
        >
          <span class="aligned">
            Unfold column
            <DocumentationBlock>
              You are about to unfold a column containing array values.
              <br />
              <br />
              More information about column unfolding can be found in our
              <a
                href="https://debiai.irt-systemx.fr/dashboard/unfolding"
                target="_blank"
              >
                online documentation
              </a>
            </DocumentationBlock>
          </span>

          <button
            class="red"
            @click="columnToUnfoldVerticallyOrHorizontally = null"
          >
            Cancel
          </button>
        </h3>

        <!-- <p>Do you want to unfold it vertically or horizontally?</p> -->

        <div
          id="verticalUnfold"
          class="unfoldMethod"
        >
          <h4 class="aligned spaced">
            Unfold vertically

            <AvailableTag available />
          </h4>
          Add one new line for each elements in the array.
          <br />
          <button @click="unfoldVertically(columnToUnfoldVerticallyOrHorizontally)">
            Add new lines
          </button>
        </div>

        <div
          id="horizontalUnfold"
          class="unfoldMethod"
        >
          <h4 class="aligned spaced">
            Unfold horizontally

            <AvailableTag
              :available="columnToUnfoldVerticallyOrHorizontally.arrayColumnSizeNumber > 0"
              :notAvailableColor="'var(--greyDarker)'"
            />
          </h4>
          Add a column for each element of the array.
          <br />

          <button
            v-if="columnToUnfoldVerticallyOrHorizontally.arrayColumnSizeNumber"
            @click="unfoldArrayHorizontally(columnToUnfoldVerticallyOrHorizontally)"
          >
            Add
            {{ columnToUnfoldVerticallyOrHorizontally.arrayColumnSizeNumber }}
            new columns
          </button>

          <p
            v-else
            class="unfoldingNotAvailable"
          >
            The column {{ columnToUnfoldVerticallyOrHorizontally.label }} cannot be unfolded
            horizontally, <br />
            the size of the array elements are not constant.
          </p>
        </div>
      </div>
    </Modal>

    <!-- Horizontal unfolding error message-->
    <Modal
      @close="horizontalUnfoldErrorMessage = ''"
      v-if="horizontalUnfoldErrorMessage"
    >
      <div id="horizontalUnfoldErrorMessage">
        <h3
          class="aligned spaced"
          style="gap: 20px"
        >
          <span class="aligned">
            Horizontal unfolding error
            <DocumentationBlock>
              The column cannot be unfolded horizontally.
              <br />
              <br />
              More information about column unfolding can be found in our
              <a
                href="https://debiai.irt-systemx.fr/dashboard/unfolding"
                target="_blank"
              >
                online documentation
              </a>
            </DocumentationBlock>
          </span>

          <button
            class="red"
            @click="horizontalUnfoldErrorMessage = ''"
          >
            Close
          </button>
        </h3>
        <p>{{ horizontalUnfoldErrorMessage }}</p>
      </div>

      <button @click="horizontalUnfoldErrorMessage = ''">Close</button>
    </Modal>

    <!-- Select columns to unfold -->
    <Modal
      @close="columnIndexToSelectHorizontalColumns = null"
      v-if="columnIndexToSelectHorizontalColumns"
    >
      <div id="selectColumnsToUnfold">
        <h3
          class="aligned spaced"
          style="gap: 20px"
        >
          <span class="aligned">
            Select the keys to unfold
            <DocumentationBlock>
              You are about to unfold a column containing a dictionary.
              <br />
              <br />
              More information about column unfolding can be found in our
              <a
                href="https://debiai.irt-systemx.fr/dashboard/unfolding"
                target="_blank"
              >
                online documentation
              </a>
            </DocumentationBlock>
          </span>

          <button
            class="red"
            @click="columnIndexToSelectHorizontalColumns = null"
          >
            Cancel
          </button>
        </h3>
        <p>
          You are about to unfold a column containing a dictionary.
          <br />
          Please select the columns you want to unfold.
        </p>

        <div id="columnsToUnfold">
          <div
            v-for="(column, index) in newPossibleColumns"
            :key="index"
            class="columnToUnfold"
          >
            <input
              type="checkbox"
              :id="column"
              v-model="column.selected"
            />
            <label>{{ column.key }}</label>
          </div>
        </div>

        <button @click="unfoldDictHorizontally(columnIndexToSelectHorizontalColumns)">
          Add the new columns
        </button>
      </div>
    </Modal>
  </div>
</template>

<script>
export default {
  name: "ColumnUnfoldingMenu",
  data() {
    return {
      // Array columns
      columnToUnfoldVerticallyOrHorizontally: null,

      // Dict columns
      columnIndexToSelectHorizontalColumns: null,
      newPossibleColumns: [],
      horizontalUnfoldErrorMessage: "",
    };
  },
  props: {
    data: { type: Object, required: true },
  },
  created() {},
  methods: {
    unfoldColumn(columnIndex) {
      const column = this.data.getColumn(columnIndex);
      if (!column) return;

      if (column.typeText === "Array") {
        // Fold if the column is already unfolded
        if (column.unfolded) this.data.foldVertically(columnIndex);
        else if (column.unfoldedHorizontally) this.data.foldHorizontally(columnIndex);
        // Ask if we unfold vertically or horizontally
        else this.columnToUnfoldVerticallyOrHorizontally = column;
      } else if (column.typeText === "Dict") {
        // Fold if the column is already unfolded
        if (column.unfoldedHorizontally) {
          this.data.foldHorizontally(columnIndex);
          return;
        }

        // Get the possible columns to unfold
        const newPossibleColumns = column.getPossibleColumnsToUnfold();
        if (newPossibleColumns.error) {
          this.horizontalUnfoldErrorMessage = newPossibleColumns.error;
          return;
        }

        // Ask what columns to select
        this.newPossibleColumns = newPossibleColumns.keys.map((key) => {
          return {
            selected: true,
            key: key,
          };
        });
        this.columnIndexToSelectHorizontalColumns = columnIndex;
      }
    },
    unfoldVertically() {
      this.data.unfoldVertically(this.columnToUnfoldVerticallyOrHorizontally.index);
      this.columnToUnfoldVerticallyOrHorizontally = null;
    },
    unfoldDictHorizontally(columnIndex) {
      const columnsToUnfold = this.newPossibleColumns
        .filter((column) => column.selected)
        .map((column) => column.key);
      this.data.unfoldDictHorizontally(columnIndex, columnsToUnfold);
      this.columnIndexToSelectHorizontalColumns = null;
      this.newPossibleColumns = [];
    },
    unfoldArrayHorizontally(column) {
      this.data.unfoldArrayHorizontally(column.index);
      this.columnToUnfoldVerticallyOrHorizontally = null;
    },
  },
  computed: {
    unfoldCounter() {
      return this.$store.state.StatisticalAnalysis.unfoldCounter;
    },
  },
  watch: {
    unfoldCounter() {
      // Update the unfolded column
      const columnIndex = this.$store.state.StatisticalAnalysis.unfoldedColumnIndex;
      this.unfoldColumn(columnIndex);
    },
  },
};
</script>

<style scoped lang="scss">
#ColumnUnfoldingMenu {
  #verticalOrHorizontalUnfoldingMenu {
    text-align: left;
    .unfoldMethod {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin: 20px 15px;
      padding: 20px 15px;
      border-radius: 5px;
      border: 1px solid var(--greyDarker);

      .unfoldingNotAvailable {
        color: var(--greyDarker);
        font-weight: bold;
        margin: 0;
      }
    }
  }

  #selectColumnsToUnfold {
    text-align: left;
    #columnsToUnfold {
      display: flex;
      flex-wrap: wrap;
      .columnToUnfold {
        display: flex;
        align-items: center;
        margin: 5px;
      }
    }
  }
}
</style>
