#!/usr/bin/python

import math
import re
import numpy as np

import inkscapeMadeEasy.inkscapeMadeEasy_Base as inkBase
import inkscapeMadeEasy.inkscapeMadeEasy_Draw as inkDraw
import inkscapeMadeEasy.inkscapeMadeEasy_Plot as inkPlot


def findMinMaxStep(data, step):
    ''' returns the limits of the data, such that the data fits the interval and the limits are multiples of step'''
    maximum = math.ceil(max(data) / step) * step
    mininum = math.floor(min(data) / step) * step
    return np.array([mininum, maximum])


class BodePlot(inkBase.inkscapeMadeEasy):
    def __init__(self):
        inkBase.inkscapeMadeEasy.__init__(self)

        self.arg_parser.add_argument("--tab", type=str, dest="tab", default="object")
        self.arg_parser.add_argument("--subTab_confPlot", type=str, dest="subTab_confPlot", default="object")

        self.arg_parser.add_argument("--numerator", type=str, dest="numerator", default="1")
        self.arg_parser.add_argument("--denominator", type=str, dest="denominator", default="1 1")
        self.arg_parser.add_argument("--nPoints", type=int, dest="nPoints", default=20)

        self.arg_parser.add_argument("--plotGain", type=self.bool, dest="plotGain", default=True)
        self.arg_parser.add_argument("--plotPhase", type=self.bool, dest="plotPhase", default=True)
        self.arg_parser.add_argument("--plotZP", type=self.bool, dest="plotZP", default=True)
        self.arg_parser.add_argument("--writeEqn", type=self.bool, dest="writeEqn", default=True)

        # FOR CONTINUOUS TIME BODE PLOT
        self.arg_parser.add_argument("--fMinS", type=float, dest="fMinS", default=0.01)
        self.arg_parser.add_argument("--fMaxS", type=float, dest="fMaxS", default=1000)

        # FOR DISCRITE TIME BODE PLOT
        self.arg_parser.add_argument("--fMaxZ", type=str, dest="fMaxZ", default='maxSampling')
        self.arg_parser.add_argument("--fTickStep", type=float, dest="fTickStep", default='0.5')

        self.arg_parser.add_argument("--fScale", type=float, dest="fScale", default=5)
        self.arg_parser.add_argument("--fTicks", type=self.bool, dest="fTicks", default=False)
        self.arg_parser.add_argument("--fGrid", type=self.bool, dest="fGrid", default=False)
        self.arg_parser.add_argument("--fUnit", type=str, dest="fUnit", default='radS')
        self.arg_parser.add_argument("--fLabel", type=str, dest="fLabel", default='lower')
        self.arg_parser.add_argument("--fLabelCustom", type=str, dest="fLabelCustom", default='freq.')

        self.arg_parser.add_argument("--generalAspectFactor", type=float, dest="generalAspectFactor", default=1.0)

        # gain
        self.arg_parser.add_argument("--yMaxGain", type=float, dest="yMaxGain", default=2.0)
        self.arg_parser.add_argument("--gLabel", type=str, dest="gLabel", default='lower')
        self.arg_parser.add_argument("--gLabelCustom", type=str, dest="gLabelCustom", default='freq.')
        self.arg_parser.add_argument("--gUnit", type=str, dest="gUnit", default='log10')
        self.arg_parser.add_argument("--yTicksGain", type=self.bool, dest="yTicksGain", default=False)
        self.arg_parser.add_argument("--yTickStepGain", type=float, dest="yTickStepGain", default=0.5)
        self.arg_parser.add_argument("--yScaleGain", type=float, dest="yScaleGain", default=10)
        self.arg_parser.add_argument("--yGridGain", type=self.bool, dest="yGridGain", default=False)

        # phase
        self.arg_parser.add_argument("--pLabel", type=str, dest="pLabel", default='lower')
        self.arg_parser.add_argument("--pLabelCustom", type=str, dest="pLabelCustom", default='freq.')
        self.arg_parser.add_argument("--pUnit", type=str, dest="pUnit", default='deg')
        self.arg_parser.add_argument("--yTicksPhase", type=self.bool, dest="yTicksPhase", default=False)
        self.arg_parser.add_argument("--yTickStepPhaseDeg", type=float, dest="yTickStepPhaseDeg", default=45)
        self.arg_parser.add_argument("--yScalePhase", type=float, dest="yScalePhase", default=10)
        self.arg_parser.add_argument("--yGridPhase", type=self.bool, dest="yGridPhase", default=False)

        # zero/Poles
        self.arg_parser.add_argument("--markerAspectFactor", type=float, dest="markerAspectFactor", default=1.0)
        self.arg_parser.add_argument("--ZPScale", type=float, dest="ZPScale", default=5)
        self.arg_parser.add_argument("--ZPTicks", type=self.bool, dest="ZPTicks", default=True)
        self.arg_parser.add_argument("--ZPGrid", type=self.bool, dest="ZPGrid", default=True)
        self.arg_parser.add_argument("--ZPTickStep", type=float, dest="ZPTickStep", default=1)

        self.arg_parser.add_argument("--zeroColor", type=str, dest="zeroColor", default='blue')
        self.arg_parser.add_argument("--zeroColorPicker", type=str, dest="zeroColorPicker", default='0')
        self.arg_parser.add_argument("--poleColor", type=str, dest="poleColor", default='red')
        self.arg_parser.add_argument("--poleColorPicker", type=str, dest="poleColorPicker", default='0')

        # FOR DISCRITE TIME H(z) only
        self.arg_parser.add_argument("--drawUnitCircle", type=self.bool, dest="drawUnitCircle", default=True)

        # equation
        self.arg_parser.add_argument("--eqnPrecision", type=int, dest="eqnPrecision", default=2)
        self.arg_parser.add_argument("--eqnSimplifyOne", type=self.bool, dest="eqnSimplifyOne", default=False)
        self.arg_parser.add_argument("--eqnSimplifySZ0", type=self.bool, dest="eqnSimplifySZ0", default=False)
        self.arg_parser.add_argument("--eqnHideZeroTerms", type=self.bool, dest="eqnHideZeroTerms", default=False)
        self.arg_parser.add_argument("--eqnNormalizeDen", type=self.bool, dest="eqnNormalizeDen", default=False)

        # FOR CONTINUOUS TIME H(s) only
        self.arg_parser.add_argument("--eqnSimplifySZ1", type=self.bool, dest="eqnSimplifySZ1", default=False)

    def effect(self):

        so = self.options
        so.tab = so.tab.replace('"', '')  # removes de exceeding double quotes from the string

        root_layer = self.document.getroot()

        if so.tab.startswith('BodePlot_S'):
            self.typeTime = 'continuous'

        if so.tab.startswith('BodePlot_Z'):
            self.typeTime = 'discrete'

        if not inkDraw.useLatex:
            self.useLatex = False
        else:
            self.useLatex = True


        # colors
        [zeroColor, _] = inkDraw.color.parseColorPicker(so.zeroColor, so.zeroColorPicker)
        [poleColor, _] = inkDraw.color.parseColorPicker(so.poleColor, so.poleColorPicker)

        # sets the position to the viewport center, round to next 10.
        position = [self.svg.namedview.center[0], self.svg.namedview.center[1]]
        position[0] = int(math.ceil(position[0] / 10.0)) * 10
        position[1] = int(math.ceil(position[1] / 10.0)) * 10

        # line style
        lineWidthPlot = so.generalAspectFactor * min(so.fScale, so.yScaleGain) / 30.0
        lineColor = inkDraw.color.defined('blue')
        lineStylePlot = inkDraw.lineStyle.set(lineWidth=lineWidthPlot, lineColor=lineColor)

        numerator = np.array([float(x) for x in so.numerator.replace(',', ' ').split()])
        denominator = np.array([float(x) for x in so.denominator.replace(',', ' ').split()])

        extraTextfreq = ''

        #createLAbels
        if self.useLatex:
            [fLabel, gLabel, pLabel] = self.createLabelsLatex()
        else:
            [fLabel, gLabel, pLabel] = self.createLabelsNoLatex()


        if so.eqnNormalizeDen:
            a0=denominator[0]
            numerator/=a0
            denominator/=a0

        if self.typeTime == 'continuous':
            [freqData, Hresponse] = self.Bode_S(numerator, denominator)
            freqLogScale = True
            fTickStep = 1
            extraTextfreq = ''

        if self.typeTime == 'discrete':
            [freqData, Hresponse] = self.Bode_Z(numerator, denominator)
            freqLogScale = False
            fTickStep = so.fTickStep

            if so.fUnit == 'freqRad':
                if self.useLatex:
                    extraTextfreq = r'\pi'
                else:
                    extraTextfreq = 'π'
            else:
                extraTextfreq = ''

        # write equation
        signFunc = lambda x: ('+', '-')[x < 0]
        if so.writeEqn:
            if self.useLatex:
                if self.typeTime == 'continuous':
                    textH = r'$H(s)=\displaystyle\frac'
                if self.typeTime == 'discrete':
                    textH = r'$H(z)=\displaystyle\frac'

                for poly in [numerator,denominator]:
                    textPoly=''
                    for i,x in enumerate(poly):
                        if x == 0 and so.eqnHideZeroTerms:
                            continue

                        # s^n or z^{-n}
                        if self.typeTime == 'continuous':
                            n = len(poly) - 1 - i
                        else:
                            n=i

                        if so.eqnSimplifySZ0 and n==0:
                            szN=''
                        else:
                            if self.typeTime == 'continuous':
                                if n==1 and so.eqnSimplifySZ1:
                                    szN = 's'
                                else:
                                    szN = 's^{%d}' % n
                            if self.typeTime == 'discrete':
                                if n==1 and so.eqnSimplifySZ1:
                                    szN = 'z'
                                else:
                                    if n==0:
                                        szN = 'z^{%d}' % n
                                    else:
                                        szN = 'z^{-%d}' % n

                        sign = signFunc(x)

                        if abs(x)==1.0 and so.eqnSimplifyOne:
                            coef = ''
                        else:
                            coef = ('{:.%df}' % so.eqnPrecision).format(abs(x))

                        textPoly += sign + coef + szN

                        if textPoly.endswith('+') or textPoly.endswith('-'):
                            textPoly +=('{:.%df}' % so.eqnPrecision).format(1.0)

                    # removes '+' from first coef.
                    if textPoly.startswith('+'):
                        textPoly = textPoly[1:]

                    textH += '{' + textPoly + '}'

                textH +='$'

            inkDraw.text.latex(self, root_layer, textH, position, fontSize=5*so.generalAspectFactor)

        # abs value plot
        if so.plotGain:

            # limit gain response
            gainData = np.absolute(Hresponse)
            gainLimitReached = max(gainData > so.yMaxGain)
            gainData[gainData > so.yMaxGain] = so.yMaxGain

            if gainLimitReached and so.plotPhase and so.plotPhase:
                inkDraw.text.write(self, 'Warning: Some gain values exceeded \'Gain plot limit\'=%f.\n Plot will be truncated.' % (so.yMaxGain),
                                   position, root_layer, fontSize=5)

            if so.gUnit == 'dB':
                gainData = 20 * np.log10(gainData)
                ylog = False
                ylim = [min(gainData), 0]
                yTickStepGain = so.yTickStepGain
                yScaleGain = so.yScaleGain
            if so.gUnit == 'linear':
                ylog = False
                yTickStepGain = so.yTickStepGain
                ylim = findMinMaxStep(gainData, yTickStepGain)
                ylim[0] = 0
                yScaleGain = so.yScaleGain
            if so.gUnit == 'log10':
                ylog = True
                ylim = None
                yTickStepGain = 1  # does not matter
                yScaleGain = so.yScaleGain

            if so.gUnit == 'dB':
                extraDistY = 1.0
            else:
                extraDistY = 0.0

            [graph, limits, origin] = inkPlot.plot.cartesian(self, root_layer, freqData, gainData, position, xLabel=fLabel, yLabel=gLabel,
                                                             xlog10scale=freqLogScale, ylog10scale=ylog, xTicks=so.fTicks, yTicks=so.yTicksGain,
                                                             xTickStep=fTickStep, yTickStep=yTickStepGain, xScale=so.fScale, yScale=yScaleGain,
                                                             xGrid=so.fGrid, yGrid=so.yGridGain, xExtraText=extraTextfreq,
                                                             generalAspectFactorAxis=so.generalAspectFactor, lineStylePlot=lineStylePlot,
                                                             forceYlim=ylim, ExtraLengthAxisY=extraDistY)

            position = [position[0], position[1] - limits[3][1] + limits[2][1]]

        # adjust so.generalAspectFactor so that we get the same text size on both plots
        so.generalAspectFactor = so.generalAspectFactor * min(so.fScale, so.yScaleGain) / min(so.fScale, so.yScalePhase)

        # phase in degrees
        if so.plotPhase:
            phaseData = np.angle(Hresponse) * 180.0 / math.pi
            # find limits multiples of so.yTickStepPhaseDeg
            ylim = findMinMaxStep(phaseData, so.yTickStepPhaseDeg)

            if so.pUnit == 'deg':
                yTick = so.yTickStepPhaseDeg
                extraTextPhase=''
            if so.pUnit == 'rad':
                phaseData = phaseData * math.pi / 180.0
                yTick = so.yTickStepPhaseDeg * math.pi / 180.0
                ylim = ylim * math.pi / 180.0
                extraTextPhase=''
            if so.pUnit == 'radPi':
                phaseData = phaseData/ 180.0
                yTick = so.yTickStepPhaseDeg / 180.0
                ylim = ylim / 180.0
                if self.useLatex:
                    extraTextPhase = r'\pi'
                else:
                    extraTextPhase = 'π'

            if ylim[1] == 0.0:
                extraDistY = 1.0
            else:
                extraDistY = 0.0

            # phase plot
            [graph, limits, origin] = inkPlot.plot.cartesian(self, root_layer, freqData, phaseData, position, xLabel=fLabel, yLabel=pLabel,
                                                             xlog10scale=freqLogScale, ylog10scale=False, xTicks=so.fTicks, yTicks=so.yTicksPhase,
                                                             xTickStep=fTickStep, yTickStep=yTick, xScale=so.fScale, yScale=so.yScalePhase,
                                                             xExtraText=extraTextfreq, yExtraText=extraTextPhase, xGrid=so.fGrid, yGrid=so.yGridPhase,
                                                             generalAspectFactorAxis=so.generalAspectFactor, lineStylePlot=lineStylePlot,
                                                             forceYlim=ylim, ExtraLengthAxisY=extraDistY)

            position = [position[0], position[1] - limits[3][1] + limits[2][1]]

        # zeros and poles
        if so.plotZP:
            [zeros, poles] = self.zero_and_pole(numerator, denominator)

            # find limits of zeros and poles
            temp = np.concatenate((zeros, poles))

            if len(temp) == 0:
                inkDraw.text.write(self, 'Warning: Transfer funcion has no zeros and no poles.\n Please check the coefficients', position, root_layer,
                                   fontSize=5)
                return
            RealLim = np.array([min(np.real(temp)), max(np.real(temp))])
            ImagLim = np.array([min(np.imag(temp)), max(np.imag(temp))])

            if RealLim[0] == RealLim[1]:
                RealLim += [- so.ZPTickStep / 2.0, so.ZPTickStep / 2.0]
            if ImagLim[0] == ImagLim[1]:
                ImagLim += [- so.ZPTickStep / 2.0, so.ZPTickStep / 2.0]

            if self.typeTime == 'continuous':
                # ensures one of the limits is the Re or Im axis
                ImagLim = [min(ImagLim[0], 0), max(ImagLim[1], 0)]
                RealLim = [min(RealLim[0], 0), max(RealLim[1], 0)]

            if self.typeTime == 'discrete':
                # ensures one of the limits is the Re or Im axis
                ImagLim = [min(ImagLim[0], -1), max(ImagLim[1], 1)]
                RealLim = [min(RealLim[0], -1), max(RealLim[1], 1)]

            markSize = 2 * lineWidthPlot * so.markerAspectFactor

            poleStyle = inkDraw.lineStyle.set(lineWidth=lineWidthPlot, lineColor=poleColor)
            zeroStyle = inkDraw.lineStyle.set(lineWidth=lineWidthPlot, lineColor=zeroColor)

            [graph, _, origin] = inkPlot.axis.cartesian(self, root_layer, xLim=RealLim, yLim=ImagLim, position=position, xLabel='Re', yLabel='Im',
                                                        xTicks=so.ZPTicks, yTicks=so.ZPTicks, xTickStep=so.ZPTickStep, yTickStep=so.ZPTickStep,
                                                        xScale=so.ZPScale, yScale=so.ZPScale, xGrid=so.ZPGrid, yGrid=so.ZPGrid)

            # add zeros and poles
            zeroPoleGroup = self.createGroup(graph, 'ZeroPoles')
            for z in zeros:
                zScaled = np.array([np.real(z), np.imag(z)]) * (so.ZPScale / so.ZPTickStep)
                inkDraw.circle.centerRadius(zeroPoleGroup, centerPoint=zScaled, radius=markSize, offset=[0, 0], lineStyle=zeroStyle)

            for p in poles:
                pScaled = np.array([np.real(p), np.imag(p)]) * (so.ZPScale / so.ZPTickStep)
                inkDraw.line.relCoords(zeroPoleGroup, [[-markSize, -markSize], [2 * markSize, 2 * markSize]], offset=pScaled, lineStyle=poleStyle)
                inkDraw.line.relCoords(zeroPoleGroup, [[-markSize, markSize], [2 * markSize, -2 * markSize]], offset=pScaled, lineStyle=poleStyle)

            if self.typeTime == 'discrete' and so.drawUnitCircle:
                radius = 1.0 * so.ZPScale / so.ZPTickStep
                dashedLineStyle = inkDraw.lineStyle.set(lineWidth=lineWidthPlot / 2.0, lineColor=inkDraw.color.defined('black'), fillColor=None,
                                                        strokeDashArray='2, 2')
                inkDraw.circle.centerRadius(zeroPoleGroup, centerPoint=[0, 0], radius=radius, offset=[0, 0], label='circle',
                                            lineStyle=dashedLineStyle)

    def createLabelsLatex(self):
        """
        create axis labels
        :return:
        """
        so = self.options
        # ------------
        # CONTINUOUS TIME
        # ------------
        if self.typeTime == 'continuous':
            # frequency symbol
            if so.fLabel.lower() == 'custom':
                fSymbol = so.fLabelCustom
            else:
                if so.fUnit == 'hz':
                    if so.fLabel.lower() == 'upper':
                        fSymbol = 'F'
                    else:
                        fSymbol = 'f'
                if so.fUnit == 'rad/s':
                    if so.fLabel.lower() == 'upper':
                        fSymbol = r'\Omega'
                    else:
                        fSymbol = r'\omega'

            # frequency response symbol
            if so.fUnit == 'hz':
                respFreq = r'H(j2\pi ' + fSymbol + ')'
            if so.fUnit == 'rad/s':
                respFreq = 'H(j' + fSymbol + ')'

            # units
            if so.fUnit == 'hz':
                freqUnit = r' (\si{\hertz})'
            if so.fUnit == 'rad/s':
                freqUnit = r' (\si{\rad\per\second})'
        # ------------
        # DISCRETE TIME
        # ------------
        if self.typeTime == 'discrete':
            if so.fLabel.lower() == 'custom':
                fSymbol = so.fLabelCustom
            else:
                if so.fLabel.lower() == 'upper':
                    fSymbol = r'\Omega'
                else:
                    fSymbol = r'\omega'

            # frequency response symbol
            respFreq = r'H(e^{j' + fSymbol + '})'

            # units
            if so.fUnit == 'freqRad':
                freqUnit = r' (\si{\rad\per sample})'
            if so.fUnit == 'freqNorm':
                freqUnit = r' (\times \pi \si{\rad\per sample})'

        # GAIN AND PHASE UNITS

        if so.pUnit == 'deg':
            pUnit = r' (\si\degree)'
        if so.pUnit == 'rad' or so.pUnit == 'radPi':
            pUnit = r' (\si\rad)'

        if so.gUnit == 'dB':
            gUnit = r' (\text{dB})'
        else:
            gUnit = r' '

        # build tuples (symbol, unit)
        fLabel = '$' + fSymbol + freqUnit + '$'

        if so.gLabel == 'custom':
            gLabel = '$' + so.gLabelCustom + gUnit + '$'
        else:
            gLabel = '$' + '|%s|' % respFreq + gUnit + '$'

        if so.pLabel == 'custom':
            pLabel = '$' + so.pLabelCustom + pUnit + '$'
        else:
            pLabel = '$' + r'\phase{%s}' % respFreq + pUnit + '$'

        return [fLabel, gLabel, pLabel]

    def createLabelsNoLatex(self):
        """
        create axis labels
        :return:
        """
        so = self.options
        # ------------
        # CONTINUOUS TIME
        # ------------
        if self.typeTime == 'continuous':
            # frequency symbol
            if so.fLabel.lower() == 'custom':
                fSymbol = so.fLabelCustom
            else:
                if so.fUnit == 'hz':
                    if so.fLabel.lower() == 'upper':
                        fSymbol = 'F'
                    else:
                        fSymbol = 'f'
                if so.fUnit == 'rad/s':
                    if so.fLabel.lower() == 'upper':
                        fSymbol = 'Ω'
                    else:
                        fSymbol = 'ω'

            # frequency response symbol
            if so.fUnit == 'hz':
                respFreq = 'H(j2π' + fSymbol + ')'
            if so.fUnit == 'rad/s':
                respFreq = 'H(j' + fSymbol + ')'

            # units
            if so.fUnit == 'hz':
                freqUnit = ' (Hz)'
            if so.fUnit == 'rad/s':
                freqUnit = ' (rad/s)'
        # ------------
        # DISCRETE TIME
        # ------------
        if self.typeTime == 'discrete':
            if so.fLabel.lower() == 'custom':
                fSymbol = so.fLabelCustom
            else:
                if so.fLabel.lower() == 'upper':
                    fSymbol = 'Ω'
                else:
                    fSymbol = 'ω'

            # frequency response symbol
            respFreq = 'H[exp(j' + fSymbol + ')]'

            # units
            if so.fUnit == 'freqRad':
                freqUnit = ' (rad/sample)'
            if so.fUnit == 'freqNorm':
                freqUnit = ' (xπ  rad/sample)'

        # GAIN AND PHASE UNITS

        if so.pUnit == 'deg':
            pUnit = ' (°)'
        if so.pUnit == 'rad':
            pUnit = ' (rad)'

        if so.gUnit == 'dB':
            gUnit = ' (dB)'
        else:
            gUnit = ' '

        # build tuples (symbol, unit)
        fLabel = fSymbol + freqUnit

        if so.gLabel == 'custom':
            gLabel = so.gLabelCustom + gUnit
        else:
            gLabel = '|%s|' % respFreq + gUnit

        if so.pLabel == 'custom':
            pLabel = so.pLabelCustom +  pUnit
        else:
            pLabel = '∠' + respFreq + pUnit

        return [fLabel, gLabel, pLabel]

    def Bode_S(self, numerator, denominator):
        # computes the frequency response of H(s)
        # returns:
        # xlabel: string for freq axis label
        # freqData: frequency data for x axis
        # Hresponse: values of H(j\Omega)

        so = self.options
        # generate x data
        freqData = np.logspace(so.fMinS, so.fMaxS, so.nPoints)

        if so.fUnit == 'rad/s':
            freqDataRadS = freqData
        if so.fUnit == 'hz':
            freqDataRadS = freqData * 2 * math.pi  # convert hertz to rad/s

        # build s values
        sData = freqDataRadS * 1j
        # generate y data
        num = np.polyval(np.array(numerator), sData)
        den = np.polyval(np.array(denominator), sData)

        Hresponse = np.divide(num, den)

        return [freqData, Hresponse]

    def Bode_Z(self, numerator, denominator):
        # computes the frequency response of H(z)
        # returns:
        # xlabel: string for freq axis label
        # freqData: frequency data for x axis
        # Hresponse: values of H(e^{j \omega})

        so = self.options
        # generate x data
        if so.fMaxZ == 'maxSampling':
            freqDataRad = np.linspace(0, 2 * math.pi, so.nPoints)  # pi = nyquist
        else:
            freqDataRad = np.linspace(0, math.pi, so.nPoints)  # pi = nyquist

        if so.fUnit == 'freqRad':
            freqData = freqDataRad / math.pi  # divides by pi bc the plot will be in function of pi.
            xlabel = r'$%s$ (\si{\rad\per sample})' % so.fLabel
        if so.fUnit == 'freqNorm':
            freqData = freqDataRad / math.pi  # convert from omega in rad to omega normalized (1.0 = nyquist)
            xlabel = r'$%s$ ($\times \pi$ \si{\rad\per sample})' % so.fLabel

        zData = np.exp(-1j * freqDataRad)  # negative angles because the polinomials are powers of z^{-1}
        # generate y data

        num = np.polyval(np.array(numerator[::-1]), zData)  # reverses the numerator bc polyval assumes first the highest powers.
        den = np.polyval(np.array(denominator[::-1]), zData)  # reverses the numerator bc polyval assumes first the highest powers.

        Hresponse = np.divide(num, den)

        return [freqData, Hresponse]

    def zero_and_pole(self, numerator, denominator):
        # computes the zeros and poles of H(s)

        # numerator,denominator:  lists with the coeficientes, in descending powers of s or increasing power of z^-1

        # returns:
        # zeros: numpy array with the zeros
        # poles: numpy array with the poles

        zeros = np.roots(np.array(numerator))
        poles = np.roots(np.array(denominator))

        return [zeros, poles]


if __name__ == '__main__':
    plot = BodePlot()
    plot.run()
