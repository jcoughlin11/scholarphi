import MuiDrawer from "@material-ui/core/Drawer";
import IconButton from "@material-ui/core/IconButton";
import ChevronRightIcon from "@material-ui/icons/ChevronRight";
import { PDFDocumentProxy } from "pdfjs-dist";
import React from "react";
import EntityPropertyEditor from "./EntityPropertyEditor";
import FeedbackButton from "./FeedbackButton";
import PaperList from "./PaperList";
import SearchResults from "./SearchResults";
import * as selectors from "./selectors";
import { Entities, PaperId, Papers, UserLibrary } from "./state";
import { Entity, EntityUpdateData } from "./types/api";
import { PDFViewer } from "./types/pdfjs-viewer";

export type DrawerMode = "open" | "closed";

interface Props {
  paperId: PaperId | undefined;
  pdfViewer: PDFViewer;
  pdfDocument: PDFDocumentProxy | null;
  mode: DrawerMode;
  papers: Papers | null;
  entities: Entities | null;
  userLibrary: UserLibrary | null;
  selectedEntityId: string | null;
  entityEditingEnabled: boolean;
  handleClose: () => void;
  handleSelectSymbol: (id: string) => void;
  handleScrollSymbolIntoView: () => void;
  handleAddPaperToLibrary: (paperId: string, paperTitle: string) => void;
  handleUpdateEntity: (entity: EntityUpdateData) => Promise<boolean>;
  handleDeleteEntity: (id: string) => Promise<boolean>;
}

export class Drawer extends React.PureComponent<Props> {
  constructor(props: Props) {
    super(props);
    this.closeDrawer = this.closeDrawer.bind(this);
  }

  componentWillUnmount() {
    const { pdfViewer } = this.props;
    if (pdfViewer != null) {
      this.removePdfPositioningForDrawerOpen(pdfViewer.container);
    }
  }

  positionPdfForDrawerOpen(
    pdfViewerContainer: HTMLElement,
    drawerContentType: string
  ) {
    pdfViewerContainer.classList.add(`drawer-${drawerContentType}`);
  }

  removePdfPositioningForDrawerOpen(pdfViewerContainer: HTMLElement) {
    pdfViewerContainer.classList.forEach((c) => {
      if (c.indexOf("drawer-") !== -1) {
        pdfViewerContainer.classList.remove(c);
      }
    });
  }

  closeDrawer() {
    if (this.props.mode !== "closed") {
      this.props.handleClose();
    }
  }

  render() {
    /**
     * The PDF viewer should know if the drawer is open so it can reposition the paper. Currently, we
     * notify the PDF viewer by adding a class, as the PDF viewer otherwise has no knowledge of the
     * state of this React application.
     */
    const {
      paperId,
      pdfViewer,
      pdfDocument,
      mode,
      entities,
      selectedEntityId,
      entityEditingEnabled,
      handleSelectSymbol,
    } = this.props;

    const feedbackContext = {
      mode,
      selectedEntityId,
    };

    let selectedEntity: Entity | null = null;
    if (entities !== null && selectedEntityId !== null) {
      selectedEntity = entities.byId[selectedEntityId] || null;
    }

    /*
     * Only one type of drawer content can appear at a time. This conditional block determines
     * which types of drawer content have precedence.
     */
    type DrawerContentType =
      | null
      | "entity-property-editor"
      | "symbol-search-results"
      | "paper-list";
    let drawerContentType: DrawerContentType = null;
    if (entityEditingEnabled === true) {
      drawerContentType = "entity-property-editor";
    } else if (
      selectors.selectedEntityType(selectedEntityId, entities) === "symbol" &&
      pdfDocument !== null
    ) {
      drawerContentType = "symbol-search-results";
    } else if (
      selectors.selectedEntityType(selectedEntityId, entities) === "citation"
    ) {
      drawerContentType = "paper-list";
    }

    if (pdfViewer != null) {
      if (mode === "open" && drawerContentType !== null) {
        this.removePdfPositioningForDrawerOpen(pdfViewer.container);
        this.positionPdfForDrawerOpen(pdfViewer.container, drawerContentType);
      } else {
        this.removePdfPositioningForDrawerOpen(pdfViewer.container);
      }
    }

    return (
      <MuiDrawer
        className="drawer"
        variant="persistent"
        anchor="right"
        /*
         * If for the drawer has been requested to open but there's nothing to show
         * in it, don't show it.
         */
        open={mode === "open" && drawerContentType !== null}
      >
        <div className="drawer__header">
          <div className="drawer__close_icon">
            <IconButton size="small" onClick={this.closeDrawer}>
              <ChevronRightIcon />
            </IconButton>
          </div>
          <FeedbackButton paperId={paperId} extraContext={feedbackContext} />
        </div>
        <div className="drawer__content">
          {drawerContentType === "symbol-search-results" && (
            <SearchResults
              pdfDocument={pdfDocument as PDFDocumentProxy}
              pageSize={4}
              entities={entities}
              selectedEntityId={selectedEntityId}
              handleSelectSymbol={handleSelectSymbol}
            />
          )}
          {drawerContentType === "paper-list" && (
            <PaperList
              papers={this.props.papers}
              userLibrary={this.props.userLibrary}
              handleAddPaperToLibrary={this.props.handleAddPaperToLibrary}
            />
          )}
          {drawerContentType === "entity-property-editor" && (
            <EntityPropertyEditor
              /*
               * When the selected entity changes, clear the property editor.
               */
              key={selectedEntityId || undefined}
              entity={selectedEntity}
              handleSaveChanges={this.props.handleUpdateEntity}
              handleDeleteEntity={this.props.handleDeleteEntity}
            />
          )}
        </div>
      </MuiDrawer>
    );
  }
}

export default Drawer;
