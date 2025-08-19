import StrategicIntelligenceEngine from '../../components/StrategicIntelligenceEngine-working';
import Navigation from '../../components/Navigation';
import { Box, Container, Text } from '@mantine/core';

export default function StrategicIntelligencePage() {
  return (
    <Box style={{ minHeight: '100vh', backgroundColor: 'var(--mantine-color-gray-0)' }}>
      <Navigation />
      <StrategicIntelligenceEngine />
      <Container>
        <Text ta="center" py={24} c="dimmed">© 2025 PM33. Strategic Intelligence Platform.</Text>
      </Container>
    </Box>
  );
}