<template>
  <div id="project">
    <!-- Settings modal -->
    <Modal
      v-if="settings && project"
      @close="settings = false"
    >
      <!-- block structure creation or display -->
      <h2 class="aligned spaced">
        Project columns
        <button
          class="red"
          @click="settings = false"
        >
          Close
        </button>
      </h2>
      <ProjectColumnsVisualization />
    </Modal>

    <!-- Header -->
    <Header
      :project="project"
      v-on:settings="settings = !settings"
      v-on:refresh="loadProject"
      v-on:deleteProject="deleteProject"
      v-on:backToProjects="backToProjects"
    />

    <!-- Project Content -->
    <transition name="fade">
      <div
        id="projectContent"
        v-if="project"
      >
        <div id="selectionAndModels">
          <!-- Data selection selection -->
          <Selections
            :project="project"
            :nbSelectedSamples="nbSelectedSamples"
            v-on:selectionSelected="selectionSelected"
            v-on:selectionDeleted="selectionDeleted"
            v-on:setSelectionIntersection="(si) => (selectionIntersection = si)"
            v-on:newSelection="loadProject"
          />

          <!-- Model selection -->
          <Models
            :project="project"
            :nbEvaluatedSamples="nbEvaluatedSamples"
            :nbSelectedSamples="nbSelectedSamples"
            :nbResults="nbResults"
            v-on:modelSelected="modelSelected"
            v-on:modelDeleted="modelDeleted"
            v-on:setCommonModelResults="(cmr) => (commonModelResults = cmr)"
          />
        </div>

        <!-- cache and Start analysis btn -->
        <div
          id="bot"
          class="card"
          style="margin: 5px"
        >
          <CachePanel :project="project" />

          <button
            id="startAnalysisBtn"
            @click="startAnalysis(false)"
            @mousedown.middle="startAnalysis(true)"
            :disabled="!readyToAnalyze"
          >
            Start analysis
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
// Components
import Header from "./Header";
import ProjectColumnsVisualization from "./projectColumns/ProjectColumnsVisualization.vue";
import Models from "./Models.vue";
import Selections from "./selections/Selections.vue";
import CachePanel from "./cache/CachePanel.vue";

// Services
import dataLoader from "@/services/dataLoader";
import samplesIdListRequester from "@/services/statistics/samplesIdListRequester";
import swal from "sweetalert";

export default {
  name: "Project",
  components: {
    Header,
    ProjectColumnsVisualization,
    Models,
    Selections,
    CachePanel,
  },
  data: () => {
    return {
      dataProviderId: null,
      projectId: null,
      project: null,
      loading: false,
      settings: false,

      // Analysis
      //    Selections
      selectedSelectionsIds: [],
      selectionIntersection: true,
      nbSelectedSamples: 0,
      //    Models
      selectedModelIds: [], // TODO: fix bug when starting analysis with a model selected, if there is an error, the model is still in the list but look unselected
      commonModelResults: true,
      nbEvaluatedSamples: 0,
      nbResults: 0,
    };
  },
  created() {
    // get data-provider ID and project ID from url path or router params
    let dataProviderId = this.$route.params.dataProviderId
      ? this.$route.params.dataProviderId
      : this.$route.query.dataProviderId;
    let projectId = this.$route.params.projectId
      ? this.$route.params.projectId
      : this.$route.query.projectId;

    // Check if we need to start analysis right away
    let startAns = this.$route.query.startAnalysis;

    if (dataProviderId && projectId) {
      this.dataProviderId = dataProviderId;
      this.projectId = projectId;
      this.$store.commit("setDataProviderId", dataProviderId);
      this.$store.commit("setProjectId", projectId);

      // Load data-provider info
      this.$backendDialog.getSingleDataInfo().then((dataInfo) => {
        this.$store.commit("setDataProviderInfo", dataInfo);
      });

      // Load the project data
      this.loadProject().then(() => {
        if (startAns) {
          console.log("Start analysis");
          let selectionIds = this.$route.query.selectionIds;
          let selectionIntersection = this.$route.query.selectionIntersection;
          let modelIds = this.$route.query.modelIds;
          let commonModelResults = this.$route.query.commonModelResults;

          // Convert str to lists
          if (selectionIds) selectionIds = selectionIds.split(".");
          if (modelIds) modelIds = modelIds.split(".");

          // Convert str to Boolean
          selectionIntersection = selectionIntersection === true;
          commonModelResults = commonModelResults === true;

          // Start analysis
          this.loadData({
            dataProviderId,
            projectId,
            selectionIds,
            selectionIntersection,
            modelIds,
            commonModelResults,
          });
        }
      });
    } else {
      console.log("No project ID or no data provider ID");
      this.$router.push("/");
    }
  },
  methods: {
    async loadProject() {
      this.project = null;
      return this.$backendDialog
        .getProject()
        .then((project) => {
          this.project = project;
          this.nbSelectedSamples = this.project.nbSamples;

          // Sort models and selections by update date
          this.project.selections = this.project.selections.sort(
            (a, b) => b.updateDate - a.updateDate
          );
          this.project.models = this.project.models.sort((a, b) => b.updateDate - a.updateDate);

          // Store some info
          this.$store.commit("setProjectColumns", this.project.columns);
          this.$store.commit("setProjectResultsColumns", this.project.resultStructure);
          this.$store.commit("setProjectName", this.project.name);

          // Change the browser title
          if (this.project.name) document.title = this.project.name;
          else document.title = this.project.id;
        })
        .catch((e) => {
          if (e.response && e.response.status === 500) {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Internal server error while loading project",
            });
          } else if (e.response && e.response.status === 404) {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Project not found",
            });
          } else {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Error while loading project",
            });
          }
          console.log(e);
          this.$router.push("/");
        });
    },

    // Analysis Parameters
    selectionSelected(selectedSelectionsIds) {
      this.selectedSelectionsIds = selectedSelectionsIds;
      this.updateNbSamples();
    },
    modelSelected(selectedModelIds) {
      this.selectedModelIds = selectedModelIds;
      this.updateNbSamples();
    },
    updateNbSamples() {
      // Get the number of samples that will be analyzed
      // Don't send request if there is no selection and model
      if (this.selectedSelections.length === 0 && this.selectedModels.length === 0) {
        this.nbSelectedSamples = this.project.nbSamples;
        this.nbEvaluatedSamples = 0;
        this.nbResults = 0;
        return;
      }

      // Send request
      const parameters = {
        analysis: { id: this.$services.uuid(), start: true, end: true },
        selectionIds: this.selectedSelections.map((s) => s.id),
        selectionIntersection: this.selectionIntersection,
        modelIds: this.selectedModels.map((m) => m.id),
        commonResults: this.commonModelResults,
      };
      this.loading = true;
      samplesIdListRequester
        .getIdList(parameters)
        .finally(() => (this.loading = false))
        .then((res) => {
          this.nbSelectedSamples = res.nbFromSelection;
          this.nbEvaluatedSamples = res.nbSamples;
          this.nbResults = res.nbFromModels;
        })
        .catch((e) => {
          console.log(e);
          this.$store.commit("sendMessage", {
            title: "error",
            msg: "Something went wrong while getting the samples list",
          });
          this.loadProject();
        });
    },

    // Analysis start
    startAnalysis({ newTab }) {
      if (newTab) {
        let routeData = this.$router.resolve({
          path: "/dataprovider/" + this.dataProviderId + "/project/" + this.projectId,
          query: {
            selectionIds: this.selectedSelectionsIds,
            selectionIntersection: this.selectionIntersection,
            modelIds: this.selectedModelIds,
            commonModelResults: this.commonModelResults,
            startAnalysis: true,
          },
        });
        window.open(routeData.href, "_blank");
      } else {
        this.loadData({
          dataProviderId: this.dataProviderId,
          projectId: this.projectId,
          selectionIds: this.selectedSelectionsIds,
          selectionIntersection: this.selectionIntersection,
          modelIds: this.selectedModelIds,
          commonModelResults: this.commonModelResults,
        });
      }
    },

    loadData({
      dataProviderId,
      projectId,
      selectionIds = [],
      selectionIntersection = false,
      modelIds = [],
      commonModelResults = false,
    }) {
      console.time("Loading data");
      this.loading = true;

      dataLoader
        .loadProjectSamples({
          selectionIds,
          selectionIntersection,
          modelIds,
          commonModelResults,
        })
        .then((data) => {
          // If no data, stop here, it has been canceled
          if (!data) {
            this.$store.commit("sendMessage", {
              title: "info",
              msg: "Analysis canceled",
            });
            return;
          }

          // Creating the data object
          this.$store.commit("setSelectionsIds", selectionIds);
          this.$store.commit("setColoredColumnIndex", 0);
          this.$store.commit("clearAllFilters");

          // Convert the lists in str for the query
          if (selectionIds && selectionIds.length > 0)
            selectionIds = selectionIds.reduce((sId, total) => total + "." + sId);
          if (modelIds && modelIds.length > 0)
            modelIds = modelIds.reduce((mId, total) => total + "." + mId);

          // Perf Log
          console.timeEnd("Loading data");

          // start analysis immediately
          this.$router.push({
            name: "dataAnalysis",
            query: {
              dataProviderId,
              projectId,
              selectionIds,
              selectionIntersection,
              modelIds,
              commonModelResults,
            },
            params: { data },
          });
        })
        .finally(() => (this.loading = false))
        .catch((e) => {
          console.log(e.response.status);
          if (e.response && e.response.status === 500) {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Internal server error while loading data",
            });
          } else if (e.response && e.response.status === 404) {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Data not found",
            });
          } else {
            this.$store.commit("sendMessage", {
              title: "error",
              msg: "Error while loading data",
            });
          }
          this.loadProject();
        });
    },

    // Other
    deleteProject() {
      swal({
        title: "Delete the project ?",
        text: "Do you really want to delete the project ? There is no way back.",
        buttons: true,
        icon: "warning",
        dangerMode: true,
      }).then((validate) => {
        if (validate)
          this.$backendDialog
            .deleteProject()
            .then(() => {
              this.$store.commit("sendMessage", {
                title: "success",
                msg: "Project deleted",
              });
              this.$router.push("/");
            })
            .catch((e) => {
              console.log(e);
              this.$store.commit("sendMessage", {
                title: "error",
                msg: "Could not delete the project",
              });
            });
      });
    },
    selectionDeleted(selectionId) {
      this.project.selections = this.project.selections.filter((s) => s.id !== selectionId);
    },
    modelDeleted(modelId) {
      this.project.models = this.project.models.filter((m) => m.id !== modelId);
    },
    backToProjects() {
      if (dataLoader.isAnalysisLoading()) {
        swal({
          title: "Cancel the analysis?",
          text: "An analysis is being started. Do you want to cancel it?",
          buttons: {
            cancel: "No",
            validate: "Yes",
          },
          icon: "warning",
          dangerMode: true,
        }).then((validate) => {
          if (validate) {
            dataLoader.cancelAnalysis();
            this.$router.push("/");
          }
        });
      } else {
        this.$router.push("/");
      }
    },
  },
  computed: {
    readyToAnalyze() {
      // return true if the ans can be run
      if (this.disabled || this.loading || this.nbSelectedSamples === 0) return false;
      if (this.selectedModelIds.length > 0 && this.nbEvaluatedSamples === 0) return false;
      return true;
    },
    selectedSelections() {
      return this.selectedSelectionsIds.map((selectedId) =>
        this.project.selections.find((s) => selectedId === s.id)
      );
    },
    selectedModels() {
      return this.selectedModelIds.map((mId) => this.project.models.find((m) => mId === m.id));
    },
  },
  watch: {
    selectionIntersection() {
      this.updateNbSamples();
    },
    commonModelResults() {
      this.updateNbSamples();
    },
  },
  beforeDestroy() {
    // We cancel the analysis if we leave the page
    if (dataLoader.isAnalysisLoading()) dataLoader.cancelAnalysis();

    // We close the swal if it is open (in case of pressing back just before the analysis start)
    try {
      swal.close();
    } catch (e) {
      console.log("Swal not open");
    }
  },
};
</script>

<style scoped lang="scss">
#project {
  text-align: left;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

#projectContent {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--greyLight);
}

#selectionAndModels {
  display: flex;
  flex: 1;
}

#bot {
  display: flex;
  justify-content: center;
  flex-direction: row;
  padding: 10px;
  gap: 30px;

  #startAnalysisBtn {
    height: 100%;
    font-size: 1.5em;
    width: 400px;
  }
}
</style>
