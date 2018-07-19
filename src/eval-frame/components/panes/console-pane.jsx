import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import deepEqual from 'deep-equal'
import Pane from './pane-container'
import CellsList from '../cells-list'

export class ConsolePaneUnconnected extends React.Component {
  static propTypes = {
    history: PropTypes.array,
  }

  shouldComponentUpdate(nextProps) {
    return (!deepEqual(this.props, nextProps)
      && nextProps.sidePaneMode === '_CONSOLE')
  }

  render() {
    return (
      <Pane paneTitle="Console" openOnMode="_CONSOLE">
        <div id="cells">
          <CellsList containingPane="CONSOLE_PANE" />
        </div>
      </Pane>
    )
  }
}

export function mapStateToProps(state) {
  return {
    sidePaneMode: state.sidePaneMode,
  }
}

export default connect(mapStateToProps)(ConsolePaneUnconnected)