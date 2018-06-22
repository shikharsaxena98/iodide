import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import OutputRow from './output-row'
import { OutputContainer } from './output-container'
import CellOutput from './cell-output'

export class CodeOutputUnconnected extends React.Component {
  static propTypes = {
    cellId: PropTypes.number.isRequired,
  }

  render() {
    return (
      <OutputContainer cellId={this.props.cellId}>
        <OutputRow cellId={this.props.cellId} rowType="sideeffect">
          <div id={`cell-${this.props.cellId}-side-effect-target`} className="side-effect-target" />
        </OutputRow>
        <OutputRow cellId={this.props.cellId} rowType="output">
          <CellOutput cellId={this.props.cellId} />
        </OutputRow>
      </OutputContainer>
    )
  }
}

export default connect()(CodeOutputUnconnected)