import {
  Page,
  PageSection,
  PageSectionVariants,
  Tab,
  Tabs,
  TabTitleText,
  Title,
} from '@patternfly/react-core';
import {useLocation, useParams, useSearchParams} from 'react-router-dom';
import {useCallback, useState} from 'react';
import RepositoriesList from 'src/routes/RepositoriesList/RepositoriesList';
import Settings from './Tabs/Settings/Settings';
import {QuayBreadcrumb} from 'src/components/breadcrumb/Breadcrumb';
import RobotAccountsList from 'src/routes/RepositoriesList/RobotAccountsList';

export default function Organization() {
  const location = useLocation();
  const {organizationName} = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  const [activeTabKey, setActiveTabKey] = useState<string>(
    searchParams.get('tab') || 'Repositories',
  );

  const onTabSelect = useCallback(
    (_event: React.MouseEvent<HTMLElement, MouseEvent>, tabKey: string) => {
      setSearchParams({tab: tabKey});
      setActiveTabKey(tabKey);
    },
    [],
  );

  const repositoriesSubNav = [
    {
      name: 'Repositories',
      component: <RepositoriesList organizationName={organizationName} />,
    },
    {
      name: 'Robot accounts',
      component: <RobotAccountsList organizationName={organizationName} />,
    },
    {
      name: 'Settings',
      component: <Settings organizationName={organizationName} />,
    },
  ];

  return (
    <Page>
      <QuayBreadcrumb />
      <PageSection
        variant={PageSectionVariants.light}
        className="no-padding-bottom"
      >
        <Title data-testid="repo-title" headingLevel="h1">
          {organizationName}
        </Title>
      </PageSection>
      <PageSection
        variant={PageSectionVariants.light}
        padding={{default: 'noPadding'}}
      >
        <Tabs activeKey={activeTabKey} onSelect={onTabSelect}>
          {repositoriesSubNav.map((nav) => (
            <Tab
              key={nav.name}
              eventKey={nav.name}
              title={<TabTitleText>{nav.name}</TabTitleText>}
            >
              {nav.component}
            </Tab>
          ))}
        </Tabs>
      </PageSection>
    </Page>
  );
}
