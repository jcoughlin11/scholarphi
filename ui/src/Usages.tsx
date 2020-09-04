import React from "react";
import * as selectors from "./selectors";
import Snippet from "./Snippet";
import { Entities } from "./state";
import { isSymbol, isTerm, Symbol, Term } from "./types/api";

interface Props {
  selectedEntityIds: string[];
  entities: Entities;
  handleJumpToEntity: (id: string) => void;
}

export class Usages extends React.PureComponent<Props> {
  render() {
    const { selectedEntityIds, entities } = this.props;
    const selectedEntityIdsWithUsages = selectedEntityIds
      .map((id) => entities.byId[id])
      .filter((e) => e !== undefined)
      .filter((e) => isTerm(e) || isSymbol(e))
      .map((e) => e as Term | Symbol)
      .map((s) => s.id);
    const usages = selectors.usages(selectedEntityIdsWithUsages, entities);

    return (
      <div className="document-snippets usages">
        <p className="drawer__content__header">Usages</p>
        {usages.map((u) => (
          <Snippet
            key={u.contextEntity.id}
            id={`usage-${u.contextEntity.id}`}
            context={u.contextEntity}
            handleJumpToContext={this.props.handleJumpToEntity}
          >
            {u.excerpt}
          </Snippet>
        ))}
      </div>
    );
  }
}

export default Usages;
